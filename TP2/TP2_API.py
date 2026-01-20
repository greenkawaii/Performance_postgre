import requests
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time
import psycopg2
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime

#Charger les variables d'environnement
load_dotenv()
ISS_api_url = os.getenv("ISS_api_url")
Mongo_url = os.getenv("M_url")
Supabase_url = os.getenv("Supabase_url")

# Afficher l'URL (masquer les identifiants)
if Mongo_url:
    print(f"URL MongoDB chargée: {Mongo_url[:30]}...{Mongo_url[-20:]}")
else:
    print("ERREUR: M_url n'est pas chargée du fichier .env")

# Constantes
DB_NAME = "ISS_DB"
COLLECTION_NAME = "ISS_loc"

#Créer la collection sur MongoDB si elle n'existe pas
def create_collection_if_not_exists(client):
    """Créer une collection uniquement si elle n'existe pas"""
    
    try:
        # Base de données et nom de collection
        db = client[DB_NAME]
        
        # Vérifier si la collection existe déjà
        if COLLECTION_NAME in db.list_collection_names():
            print(f"La collection '{COLLECTION_NAME}' existe déjà. Aucune action nécessaire.")
            return db[COLLECTION_NAME]
        
        # Créer la collection si elle n'existe pas
        collection = db.create_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' créée avec succès!")
        return collection
        
    except Exception as e:
        print(f"Erreur lors de la création de la collection: {e}")
        raise

def get_iss_data(max_retries=3, timeout=15):
    """Récupère les données actuelles de l'ISS avec retries automatiques"""
    for attempt in range(max_retries):
        try:
            response = requests.get(ISS_api_url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erreur HTTP {response.status_code}")
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s exponential backoff
                print(f"  ⚠️  Tentative {attempt + 1}/{max_retries} échouée. Nouvelle tentative dans {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Erreur lors de la requête API après {max_retries} tentatives: {e}")
                raise
    
def store_iss_data(collection, data):
    """Stocke les données ISS dans MongoDB"""
    try:
        collection.insert_one(data)
        # print(f"Données stockées: Latitude={data['iss_position']['latitude']}, Longitude={data['iss_position']['longitude']}")
    except Exception as e:
        print(f"Erreur lors du stockage des données: {e}")
        raise

def fetch_and_store_multiple(num_iterations=10, sleep_time=1):
    """Récupère et stocke les données de l'ISS plusieurs fois avec un délai entre chaque requête"""
    
    client = None
    try:
        # Connexion MongoDB
        client = MongoClient(Mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("Connecté à MongoDB Atlas!")
        
        # Créer ou récupérer la collection
        collection = create_collection_if_not_exists(client)
        
        success_count = 0
        error_count = 0
        
        # Boucle pour récupérer et stocker les données
        for i in range(num_iterations):
            print(f"\n--- Itération {i+1}/{num_iterations} ---")
            
            try:
                # Récupérer les données
                iss_data = get_iss_data()
                
                # Stocker les données
                store_iss_data(collection, iss_data)
                success_count += 1
                
            except Exception as e:
                # Afficher l'erreur mais continuer la boucle
                print(f"Erreur lors de cette itération: {e}")
                error_count += 1
                # Continuer à la prochaine itération au lieu de s'arrêter
            
            # Si ce n'est pas la dernière itération, attendre
            if i < num_iterations - 1:
                time.sleep(sleep_time)
        
        print(f"\nRécupération et stockage terminés!")
        print(f"Succès: {success_count}/{num_iterations} | Erreurs: {error_count}/{num_iterations}")
        
    except Exception as e:
        print(f"Erreur de connexion MongoDB: {e}")
    finally:
        if client:
            client.close()
            print("Connexion MongoDB fermée.")

def read_data_from_mongodb():
    """Lire toutes les données ISS de MongoDB"""
    try:
        client = MongoClient(Mongo_url, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Récupérer tous les documents
        documents = list(collection.find({}))
        print(f"\t{len(documents)} documents lus de MongoDB")
        
        client.close()
        return documents
        
    except Exception as e:
        print(f"Erreur lors de la lecture MongoDB: {e}")
        raise

def transform_to_dataframe(documents):
    """Transformer les données MongoDB en DataFrame propre avec les colonnes intéressantes"""
    try:
        # Extraire les colonnes d'intérêt
        data = []
        for doc in documents:
            data.append({
                'latitude': doc.get('iss_position', {}).get('latitude'),
                'longitude': doc.get('iss_position', {}).get('longitude'),
                'timestamp': doc.get('timestamp'),
                '_id_mongo': str(doc.get('_id'))  # Garder l'ID MongoDB pour référence
            })
        
        # Créer le DataFrame
        df = pd.DataFrame(data)
        
        # Convertir timestamp Unix (entier en secondes) en datetime
        # Le timestamp ISS est en format Unix (secondes depuis 1970)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Ajouter une colonne de timestamp de création
        df['created_at'] = datetime.now()
        
        print(f"\tDataFrame créé avec {len(df)} lignes et colonnes: {list(df.columns)}")
        print(f"\nAperçu des données:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Erreur lors de la transformation en DataFrame: {e}")
        raise

def write_to_supabase(df):
    """Écrire les données du DataFrame dans Supabase PostgreSQL sans créer de doublons"""
    try:
        # Parser l'URL Supabase
        parsed = urlparse(Supabase_url)
        
        # Connexion à Supabase
        connection = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password
        )
        cursor = connection.cursor()
        
        # Créer la table si elle n'existe pas
        create_table_query = """
        CREATE TABLE IF NOT EXISTS iss_data (
            id SERIAL PRIMARY KEY,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mongo_id TEXT UNIQUE
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'iss_data' créée/vérifiée")
        
        # Récupérer tous les mongo_ids existants pour éviter les doublons
        cursor.execute("SELECT mongo_id FROM iss_data")
        existing_mongo_ids = set(row[0] for row in cursor.fetchall())
        print(f"{len(existing_mongo_ids)} entrées existantes dans la base")
        
        # Insérer les données (sauf les doublons)
        insert_query = """
        INSERT INTO iss_data (latitude, longitude, timestamp, created_at, mongo_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        rows_inserted = 0
        rows_skipped = 0
        
        for index, row in df.iterrows():
            # Vérifier si ce mongo_id existe déjà
            if row['_id_mongo'] in existing_mongo_ids:
                rows_skipped += 1
                continue
            
            cursor.execute(insert_query, (
                row['latitude'],
                row['longitude'],
                row['timestamp'],
                row['created_at'],
                row['_id_mongo']
            ))
            rows_inserted += 1
            existing_mongo_ids.add(row['_id_mongo'])  # Ajouter à l'ensemble pour éviter les doublons dans ce batch
        
        connection.commit()
        print(f"{rows_inserted} lignes insérées | {rows_skipped} lignes ignorées (doublons)")
        
        cursor.close()
        connection.close()
        print("Connexion Supabase fermée")
        
    except Exception as e:
        print(f"Erreur lors de l'écriture dans Supabase: {e}")
        raise

def migrate_mongodb_to_supabase():
    """Pipeline complet: MongoDB → DataFrame → Supabase"""
    try:
        print("\n=== MIGRATION MONGODB -> SUPABASE ===\n")
        
        # Étape 1: Lire de MongoDB
        print("Lecture des données de MongoDB...")
        documents = read_data_from_mongodb()
        
        # Étape 2: Transformer en DataFrame
        print("\nTransformation en DataFrame...")
        df = transform_to_dataframe(documents)
        
        # Étape 3: Écrire dans Supabase
        print("\nÉcriture dans Supabase...")
        write_to_supabase(df)
        
        print("\nMigration terminée avec succès!")
        
    except Exception as e:
        print(f"\nErreur lors de la migration: {e}")
        raise
    

if __name__ == '__main__':
    try:
        # Option 1: Récupérer et stocker plusieurs fois
        # fetch_and_store_multiple(num_iterations=4, sleep_time=1)
        
        # Option 2: Migrer de MongoDB à Supabase
        fetch_and_store_multiple(num_iterations=200, sleep_time=1)
        migrate_mongodb_to_supabase()
        
    except Exception as e:
        print(f"Erreur: {e}")
        