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
                print(f"\tTentative {attempt + 1}/{max_retries} échouée. Nouvelle tentative dans {wait_time}s...")
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

def insert_into_supabase_direct(connection, iss_data):
    """Insère directement une donnée ISS dans Supabase (sans vérifier MongoDB)"""
    try:
        cursor = connection.cursor()
        
        # Préparer les données - CONVERSION CORRECTE
        latitude = float(iss_data.get('iss_position', {}).get('latitude', 0))
        longitude = float(iss_data.get('iss_position', {}).get('longitude', 0))
        timestamp = iss_data.get('timestamp')
        
        # Convertir timestamp Unix en datetime
        from datetime import datetime as dt
        if timestamp:
            timestamp_dt = dt.fromtimestamp(int(timestamp))
        else:
            timestamp_dt = None
        
        # Créer la table si elle n'existe pas (une seule fois)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS iss_data (
            id SERIAL PRIMARY KEY,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        
        # Insérer les données
        insert_query = """
        INSERT INTO iss_data (latitude, longitude, timestamp, created_at)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            latitude,
            longitude,
            timestamp_dt,
            datetime.now()
        ))
        connection.commit()
        cursor.close()
        
        return True
    except Exception as e:
        print(f"\tErreur insertion Supabase: {e}")
        return False

def pipeline_realtime(num_iterations=10, sleep_time=1):
    """
    NOUVEAU PIPELINE TEMPS RÉEL:
    API → MongoDB (immédiat) → Supabase (immédiat)
    Pas d'accumulation en RAM, sauvegarde en temps réel!
    """
    mongo_client = None
    supabase_conn = None
    
    try:
        print("\n" + "="*70)
        print("PIPELINE TEMPS RÉEL - API → MongoDB → Supabase")
        print("="*70 + "\n")
        
        # Connexion MongoDB
        print("Connexion à MongoDB...")
        mongo_client = MongoClient(Mongo_url, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        print("✓ Connecté à MongoDB Atlas!\n")
        
        # Vérifier/créer la collection ISS_loc
        mongo_collection = create_collection_if_not_exists(mongo_client)
        print()
        
        # Connexion Supabase
        print("Connexion à Supabase...")
        parsed = urlparse(Supabase_url)
        supabase_conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password
        )
        print("✓ Connecté à Supabase!\n")
        
        success_count = 0
        error_count = 0
        
        # Boucle temps réel
        for i in range(num_iterations):
            print(f"--- Itération {i+1}/{num_iterations} ---")
            
            try:
                # ÉTAPE 1: Récupérer de l'API
                print("  1️⃣  Récupération API...", end=" ")
                iss_data = get_iss_data()
                print("✓")
                
                # ÉTAPE 2: Sauvegarder dans MongoDB (immédiatement)
                print("  2️⃣  Sauvegarde MongoDB...", end=" ")
                mongo_collection.insert_one(iss_data)
                print("✓")
                
                # ÉTAPE 3: Copier dans Supabase (immédiatement)
                print("  3️⃣  Copie Supabase...", end=" ")
                if insert_into_supabase_direct(supabase_conn, iss_data):
                    print("✓")
                    success_count += 1
                else:
                    print("✗")
                    error_count += 1
                
            except Exception as e:
                print(f"\nErreur: {e}\n")
                error_count += 1
            
            # Délai avant prochaine itération
            if i < num_iterations - 1:
                time.sleep(sleep_time)
        
        print("\n" + "="*70)
        print(f"Pipeline terminé!")
        print(f"Succès: {success_count}/{num_iterations} | Erreurs: {error_count}/{num_iterations}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nErreur générale: {e}")
    finally:
        if mongo_client:
            mongo_client.close()
            print("✓ Connexion MongoDB fermée")
        if supabase_conn:
            supabase_conn.close()
            print("✓ Connexion Supabase fermée")



if __name__ == '__main__':
    try:
        # Pipeline temps réel optimal
        # API → MongoDB → Supabase (en direct, sans accumulation RAM)
        print("Démarrage du pipeline temps réel...\n")
        pipeline_realtime(num_iterations=1000, sleep_time=1)
        print("Script terminé avec succès !")
        
    except Exception as e:
        print(f"Erreur: {e}")
        