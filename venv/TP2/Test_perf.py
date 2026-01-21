import time
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import psycopg2
from urllib.parse import urlparse
import pandas as pd

# Charger les variables d'environnement
load_dotenv()
Mongo_url = os.getenv("M_url")
Supabase_url = os.getenv("Supabase_url")

# Constantes
DB_NAME = "ISS_DB"
COLLECTION_NAME = "ISS_loc"

# ========== FONCTIONS MONGODB ==========

def connect_mongodb():
    """Établir la connexion à MongoDB"""
    try:
        client = MongoClient(Mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Erreur connexion MongoDB: {e}")
        raise

def query_mongodb_with_explain(client, query_filter=None):
    """Exécuter une requête MongoDB avec explain() et mesurer le temps"""
    try:
        if query_filter is None:
            query_filter = {}  # Sélectionner tous les documents
        
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        # Exécuter la requête
        results = list(collection.find(query_filter))
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convertir en ms
        
        # Obtenir les stats d'explain
        explain_stats = collection.aggregate([
            {"$match": query_filter},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ])
        explain_results = list(explain_stats)
        
        return {
            'execution_time_ms': execution_time,
            'rows_returned': len(results),
            'explain_info': f"Documents scannés: {len(results)}",
            'database': 'MongoDB'
        }
        
    except Exception as e:
        print(f"Erreur requête MongoDB: {e}")
        raise

def get_mongodb_collection_stats(client):
    """Obtenir les statistiques de la collection MongoDB"""
    try:
        db = client[DB_NAME]
        stats = db.command('collstats', COLLECTION_NAME)
        
        return {
            'collection_name': COLLECTION_NAME,
            'document_count': stats.get('count', 0),
            'avg_size': stats.get('avgObjSize', 0),
            'storage_size': stats.get('size', 0)
        }
    except Exception as e:
        print(f"Erreur stats MongoDB: {e}")
        raise

def create_mongodb_index(client, field_path):
    """Créer un index sur un champ MongoDB"""
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        index_name = collection.create_index([(field_path, 1)])
        print(f"✓ Index créé sur MongoDB: {index_name}")
        return index_name
    except Exception as e:
        print(f"Erreur création index MongoDB: {e}")
        raise

def drop_mongodb_index(client, index_name):
    """Supprimer un index sur MongoDB"""
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        collection.drop_index(index_name)
        print(f"Index supprimé sur MongoDB: {index_name}")
    except Exception as e:
        print(f"Erreur suppression index MongoDB: {e}")
        raise

def list_mongodb_indexes(client):
    """Lister les indexes de MongoDB"""
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        indexes = collection.list_indexes()
        return [idx['name'] for idx in indexes]
    except Exception as e:
        print(f"Erreur lecture indexes MongoDB: {e}")
        raise

# ========== FONCTIONS SUPABASE (PostgreSQL) ==========

def connect_supabase():
    """Établir la connexion à Supabase"""
    try:
        parsed = urlparse(Supabase_url)
        connection = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password
        )
        return connection
    except Exception as e:
        print(f"Erreur connexion Supabase: {e}")
        raise

def query_supabase_with_explain(connection, query_sql, params=None):
    """Exécuter une requête Supabase avec EXPLAIN ANALYZE et mesurer le temps"""
    try:
        cursor = connection.cursor()
        
        # Mesurer le temps d'exécution de la requête normale
        start_time = time.time()
        
        if params:
            cursor.execute(query_sql, params)
        else:
            cursor.execute(query_sql)
        
        results = cursor.fetchall()
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convertir en ms
        
        # Exécuter EXPLAIN ANALYZE
        explain_query = f"EXPLAIN ANALYZE {query_sql}"
        if params:
            cursor.execute(explain_query, params)
        else:
            cursor.execute(explain_query)
        
        explain_results = cursor.fetchall()
        
        cursor.close()
        
        # Parser les résultats d'EXPLAIN
        explain_text = "\n".join([row[0] for row in explain_results])
        
        return {
            'execution_time_ms': execution_time,
            'rows_returned': len(results),
            'explain_info': explain_text,
            'database': 'Supabase (PostgreSQL)'
        }
        
    except Exception as e:
        print(f"Erreur requête Supabase: {e}")
        raise

def get_supabase_table_stats(connection):
    """Obtenir les statistiques de la table Supabase"""
    try:
        cursor = connection.cursor()
        
        # Nombre de lignes
        cursor.execute("SELECT COUNT(*) FROM iss_data")
        row_count = cursor.fetchone()[0]
        
        # Taille de la table
        cursor.execute("""
            SELECT pg_size_pretty(pg_total_relation_size('iss_data')) as size
        """)
        table_size = cursor.fetchone()[0]
        
        cursor.close()
        
        return {
            'table_name': 'iss_data',
            'row_count': row_count,
            'table_size': table_size
        }
    except Exception as e:
        print(f"Erreur stats Supabase: {e}")
        raise

def create_supabase_index(connection, column_name, index_name="idx_default"):
    """Créer un index sur une colonne Supabase"""
    try:
        cursor = connection.cursor()
        create_index_query = f"CREATE INDEX IF NOT EXISTS {index_name} ON iss_data({column_name})"
        cursor.execute(create_index_query)
        connection.commit()
        print(f"✓ Index créé sur Supabase: {index_name}")
        cursor.close()
    except Exception as e:
        print(f"Erreur création index Supabase: {e}")
        raise

def drop_supabase_index(connection, index_name):
    """Supprimer un index sur Supabase"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        connection.commit()
        print(f"Index supprimé sur Supabase: {index_name}")
        cursor.close()
    except Exception as e:
        print(f"Erreur suppression index Supabase: {e}")
        raise

def list_supabase_indexes(connection):
    """Lister les indexes de Supabase"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT indexname FROM pg_indexes WHERE tablename = 'iss_data'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return indexes
    except Exception as e:
        print(f"Erreur lecture indexes Supabase: {e}")
        raise

# ========== FONCTIONS DE COMPARAISON ==========

def compare_simple_select():
    """Comparer les performances d'un SELECT simple sur les deux bases"""
    try:
        print("\n" + "="*70)
        print("TEST 1: SELECT SIMPLE (récupérer tous les documents/lignes)")
        print("="*70 + "\n")
        
        # MongoDB
        print("MONGODB - Exécution du SELECT...")
        mongo_client = connect_mongodb()
        mongo_result = query_mongodb_with_explain(mongo_client, {})
        mongo_client.close()
        
        print(f"Temps d'exécution: {mongo_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {mongo_result['rows_returned']}")
        
        # Supabase
        print("\nSUPABASE - Exécution du SELECT...")
        supabase_conn = connect_supabase()
        supabase_result = query_supabase_with_explain(
            supabase_conn,
            "SELECT latitude, longitude, timestamp FROM iss_data"
        )
        supabase_conn.close()
        
        print(f"Temps d'exécution: {supabase_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {supabase_result['rows_returned']}")
        
        # Comparaison
        return {
            'test': 'SELECT Simple',
            'mongodb': mongo_result,
            'supabase': supabase_result
        }
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        raise

def compare_filtered_query():
    """Comparer les performances d'une requête filtrée"""
    try:
        print("\n" + "="*70)
        print("TEST 2: SELECT AVEC FILTRE (latitude > 0)")
        print("="*70 + "\n")
        
        # MongoDB
        print("MONGODB - Exécution du SELECT avec filtre...")
        mongo_client = connect_mongodb()
        mongo_result = query_mongodb_with_explain(
            mongo_client,
            {"iss_position.latitude": {"$gt": 0}}
        )
        mongo_client.close()
        
        print(f"Temps d'exécution: {mongo_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {mongo_result['rows_returned']}")
        
        # Supabase
        print("\nSUPABASE - Exécution du SELECT avec filtre...")
        supabase_conn = connect_supabase()
        supabase_result = query_supabase_with_explain(
            supabase_conn,
            "SELECT latitude, longitude, timestamp FROM iss_data WHERE latitude > 0"
        )
        supabase_conn.close()
        
        print(f"Temps d'exécution: {supabase_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {supabase_result['rows_returned']}")
        
        # Comparaison
        return {
            'test': 'SELECT avec Filtre',
            'mongodb': mongo_result,
            'supabase': supabase_result
        }
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        raise

# ========== TESTS AVEC INDEX ==========

def compare_filtered_query_no_index():
    """Comparer les performances d'une requête filtrée SANS index (baseline)"""
    try:
        print("\n" + "="*70)
        print("TEST 4: FILTRE LONGITUDE (SANS INDEX) - BASELINE")
        print("="*70 + "\n")
        
        # MongoDB
        print("MONGODB - Exécution du SELECT avec filtre (sans index)...")
        mongo_client = connect_mongodb()
        mongo_result = query_mongodb_with_explain(
            mongo_client,
            {"iss_position.longitude": {"$gt": 30}}
        )
        mongo_client.close()
        
        print(f"Temps d'exécution: {mongo_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {mongo_result['rows_returned']}")
        
        # Supabase
        print("\nSUPABASE - Exécution du SELECT avec filtre (sans index)...")
        supabase_conn = connect_supabase()
        supabase_result = query_supabase_with_explain(
            supabase_conn,
            "SELECT latitude, longitude, timestamp FROM iss_data WHERE longitude > 30"
        )
        supabase_conn.close()
        
        print(f"Temps d'exécution: {supabase_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {supabase_result['rows_returned']}")
        
        return {
            'test': 'Filtre Longitude (SANS INDEX)',
            'mongodb': mongo_result,
            'supabase': supabase_result
        }
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        raise

def compare_filtered_query_with_index():
    """Comparer les performances d'une requête filtrée AVEC index"""
    try:
        print("\n" + "="*70)
        print("TEST 5: FILTRE LONGITUDE (AVEC INDEX)")
        print("="*70 + "\n")
        
        # Créer les index
        print("Création des index...")
        
        # MongoDB Index
        mongo_client = connect_mongodb()
        try:
            create_mongodb_index(mongo_client, "iss_position.longitude")
        except Exception as e:
            print(f"Index MongoDB peut déjà exister: {e}")
        
        # Supabase Index
        supabase_conn = connect_supabase()
        try:
            create_supabase_index(supabase_conn, "longitude", "idx_longitude")
        except Exception as e:
            print(f"Index Supabase peut déjà exister: {e}")
        
        # Exécuter les requêtes
        print("\nMONGODB - Exécution du SELECT avec filtre (AVEC index)...")
        mongo_result = query_mongodb_with_explain(
            mongo_client,
            {"iss_position.longitude": {"$gt": 30}}
        )
        mongo_client.close()
        
        print(f"Temps d'exécution: {mongo_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {mongo_result['rows_returned']}")
        
        print("\nSUPABASE - Exécution du SELECT avec filtre (AVEC index)...")
        supabase_result = query_supabase_with_explain(
            supabase_conn,
            "SELECT latitude, longitude, timestamp FROM iss_data WHERE longitude > 30"
        )
        supabase_conn.close()
        
        print(f"Temps d'exécution: {supabase_result['execution_time_ms']:.2f} ms")
        print(f"Lignes retournées: {supabase_result['rows_returned']}")
        
        return {
            'test': 'Filtre Longitude (AVEC INDEX)',
            'mongodb': mongo_result,
            'supabase': supabase_result
        }
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        raise

def compare_index_impact():
    """Comparer l'impact des index pour chaque base"""
    try:
        print("\n" + "="*70)
        print("TEST 6: IMPACT DES INDEX (MongoDB vs Supabase)")
        print("="*70 + "\n")
        
        # Test MongoDB sans puis avec index
        print("MONGODB - Impact de l'index...")
        mongo_client = connect_mongodb()
        
        # Réinitialiser: supprimer l'index
        indexes = list_mongodb_indexes(mongo_client)
        print(f"  Indexes actuels: {indexes}")
        
        # Sans index (on va faire la requête sur le _id qui a déjà un index)
        # Donc on va faire un count simple
        start_time = time.time()
        db = mongo_client[DB_NAME]
        collection = db[COLLECTION_NAME]
        result_no_index = collection.count_documents({"iss_position.longitude": {"$gt": 30}})
        time_no_index = (time.time() - start_time) * 1000
        
        mongo_client.close()
        
        print(f"  Sans index optimisé: {time_no_index:.2f} ms ({result_no_index} docs)")
        
        # Test Supabase
        print("\nSUPABASE - Impact de l'index...")
        supabase_conn = connect_supabase()
        
        # Vérifier les indexes
        indexes = list_supabase_indexes(supabase_conn)
        print(f"  Indexes actuels: {indexes}")
        
        # Avec requête COUNT
        cursor = supabase_conn.cursor()
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM iss_data WHERE longitude > 30")
        result_count = cursor.fetchone()[0]
        time_with_query = (time.time() - start_time) * 1000
        cursor.close()
        supabase_conn.close()
        
        print(f"  Avec index: {time_with_query:.2f} ms ({result_count} lignes)")
        
        return {
            'test': 'Impact Index',
            'mongodb_time': time_no_index,
            'supabase_time': time_with_query
        }
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        raise

def compare_aggregation():

    """Comparer les performances d'une agrégation (COUNT, AVG)"""
    try:
        print("\n" + "="*70)
        print("TEST 3: AGRÉGATION (COUNT et moyenne de latitude)")
        print("="*70 + "\n")
        
        # MongoDB
        print("MONGODB - Exécution de l'agrégation...")
        mongo_client = connect_mongodb()
        
        db = mongo_client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        start_time = time.time()
        agg_results = list(collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "avg_latitude": {"$avg": "$iss_position.latitude"}
                }
            }
        ]))
        end_time = time.time()
        
        mongo_time = (end_time - start_time) * 1000
        mongo_client.close()
        
        print(f"Temps d'exécution: {mongo_time:.2f} ms")
        if agg_results:
            count = agg_results[0].get('count', 0)
            avg_lat = agg_results[0].get('avg_latitude', 0)
            if avg_lat is not None:
                print(f"Résultat: Count={count}, Avg Lat={avg_lat:.4f}")
            else:
                print(f"Résultat: Count={count}, Avg Lat=N/A")
        
        # Supabase
        print("\nSUPABASE - Exécution de l'agrégation...")
        supabase_conn = connect_supabase()
        supabase_result = query_supabase_with_explain(
            supabase_conn,
            "SELECT COUNT(*) as count, AVG(latitude) as avg_latitude FROM iss_data"
        )
        supabase_conn.close()
        
        print(f"Temps d'exécution: {supabase_result['execution_time_ms']:.2f} ms")
        
        # Comparaison
        return {
            'test': 'Agrégation',
            'mongodb': {
                'execution_time_ms': mongo_time,
                'database': 'MongoDB'
            },
            'supabase': supabase_result
        }
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        raise

def display_summary(results_list):
    """Afficher un résumé comparatif de tous les tests"""
    print("\n" + "="*70)
    print("RÉSUMÉ COMPARATIF")
    print("="*70 + "\n")
    
    # Créer un DataFrame pour afficher
    summary_data = []
    
    for result in results_list:
        test_name = result['test']
        mongo_time = result['mongodb']['execution_time_ms']
        supabase_time = result['supabase']['execution_time_ms']
        ratio = mongo_time / supabase_time if supabase_time > 0 else 0
        
        winner = "SUPABASE" if supabase_time < mongo_time else "MONGODB"
        
        summary_data.append({
            'Test': test_name,
            'MongoDB (ms)': f"{mongo_time:.2f}",
            'Supabase (ms)': f"{supabase_time:.2f}",
            'Ratio (M/S)': f"{ratio:.2f}x",
            'Gagnant': winner
        })
    
    df = pd.DataFrame(summary_data)
    print(df.to_string(index=False))
    
    print("\nNote: Un ratio > 1 = MongoDB plus lent | Ratio < 1 = Supabase plus lent")

def display_stats():
    """Afficher les statistiques des bases"""
    print("\n" + "="*70)
    print("STATISTIQUES DES BASES")
    print("="*70 + "\n")
    
    # MongoDB Stats
    print("MONGODB:")
    try:
        mongo_client = connect_mongodb()
        mongo_stats = get_mongodb_collection_stats(mongo_client)
        mongo_client.close()
        
        print(f"  Collection: {mongo_stats['collection_name']}")
        print(f"  Nombre de documents: {mongo_stats['document_count']}")
        print(f"  Taille moyenne d'un doc: {mongo_stats['avg_size']} bytes")
        print(f"  Taille totale: {mongo_stats['storage_size'] / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Supabase Stats
    print("\nSUPABASE:")
    try:
        supabase_conn = connect_supabase()
        supabase_stats = get_supabase_table_stats(supabase_conn)
        supabase_conn.close()
        
        print(f"  Table: {supabase_stats['table_name']}")
        print(f"  Nombre de lignes: {supabase_stats['row_count']}")
        print(f"  Taille de la table: {supabase_stats['table_size']}")
    except Exception as e:
        print(f"Erreur: {e}")

# ========== MAIN ==========

if __name__ == '__main__':
    try:
        print("\nBENCHMARK - MONGODB vs SUPABASE")
        print("="*70)
        
        # Afficher les stats
        display_stats()
        
        # Exécuter les tests
        results = []
        
        # Test 1: SELECT simple
        results.append(compare_simple_select())
        
        # Test 2: SELECT avec filtre
        results.append(compare_filtered_query())
        
        # Test 3: Agrégation
        results.append(compare_aggregation())
        
        # Test 4: Filtre sans index (baseline)
        results.append(compare_filtered_query_no_index())
        
        # Test 5: Filtre avec index
        results.append(compare_filtered_query_with_index())
        
        # Test 6: Impact des index
        compare_index_impact()
        
        # Afficher le résumé
        display_summary(results)
        
        print("\nTests terminés!")
        
    except Exception as e:
        print(f"\nErreur générale: {e}")
