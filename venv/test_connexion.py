from dotenv import load_dotenv
import os, base64, requests
from pymongo import MongoClient
import psycopg2
from urllib.parse import urlparse

# Charger les variables du .env
load_dotenv()

Mongo_url = os.getenv("M_url")
ISS_api_url = os.getenv("ISS_api_url")
Supabase_url = os.getenv("Supabase_url")

if __name__ == '__main__':
    #MongoDB Connection Test
    try:
        client = MongoClient(Mongo_url)
        print("Connexion réussie à MongoDB !")
    except Exception as e:
        print(f"Échec de la connexion à MongoDB : {e}")
    
    #ISS Data Connection Test
    try:
        response = requests.get(ISS_api_url)
        if response.status_code == 200:
            print("Données ISS connexion avec succès")
    except Exception as e:
        print(f"Échec de la connexion des données ISS : {response.status_code}")
    
    # Superbase Connection Test
    try:
        # Parser l'URL PostgreSQL
        parsed = urlparse(Supabase_url)
        connection = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password
        )
        print("Connexion réussie à Supabase !")
        connection.close()
    except Exception as e:
        print(f"Échec de la connexion à Supabase : {e}")