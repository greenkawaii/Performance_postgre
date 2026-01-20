# 📊 Performance MongoDB vs Supabase - Analyse Comparative

Ce projet est une étude comparative des performances entre **MongoDB** (NoSQL) et **Supabase/PostgreSQL** (SQL) pour le stockage et la récupération de données en temps réel sur la position de l'ISS.

---

## 🎯 Objectif

Analyser et comparer les performances de deux bases de données modernes :
- **MongoDB** : Base de données NoSQL orientée documents
- **Supabase** : PostgreSQL managé (SQL relationnel)

À travers différents types de requêtes et avec/sans index.

---

## 📁 Structure du Projet

```
Performance_postgre/
├── venv/
│   ├── .env                    # Variables d'environnement (à configurer)
│   ├── test_connexion.py       # Script de test de connexion
│   ├── TP2/
│   │   ├── TP2_API.py         # Pipeline de collecte et migration
│   │   └── Test_perf.py       # Suite de benchmark
│   └── ...
├── README.md                   # Ce fichier
└── .git/                       # Historique Git
```

---

## 🚀 Installation

### 1. Prérequis

- Python 3.10+
- pip (gestionnaire de paquets Python)
- Compte MongoDB Atlas
- Compte Supabase

### 2. Installation des dépendances

```bash
# Naviguer vers le dossier du projet
cd venv

# Installer les packages requis
pip install pymongo psycopg2-binary requests python-dotenv pandas
```

### 3. Configuration du fichier `.env`

Créer ou modifier le fichier `.env` dans le dossier `venv/` :

```env
# MongoDB Atlas
M_url=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/ISS_DB

# API ISS
ISS_api_url=http://api.open-notify.org/iss-now.json

# Supabase/PostgreSQL
Supabase_url=postgresql://<user>:<password>@<host>:<port>/postgres
```

---

## 📝 Fichiers Principaux

### `test_connexion.py`
**Objectif** : Tester les connexions à tous les services

```bash
python test_connexion.py
```

**Tests effectués** :
- ✅ Connexion à MongoDB Atlas
- ✅ Récupération des données ISS (API)
- ✅ Connexion à Supabase

---

### `TP2_API.py`
**Objectif** : Pipeline complet de collecte et migration des données

```bash
python TP2_API.py
```

**Workflow** :

```
1. Récupération des données ISS (API)
   ↓
2. Stockage dans MongoDB (200 itérations)
   ↓
3. Lecture depuis MongoDB
   ↓
4. Transformation en DataFrame (pandas)
   ↓
5. Écriture dans Supabase
   ↓
6. Gestion des doublons (via mongo_id)
```

**Fonctions principales** :

| Fonction | Description |
|----------|-------------|
| `fetch_and_store_multiple()` | Récupère les données ISS N fois avec délai |
| `read_data_from_mongodb()` | Lit tous les documents MongoDB |
| `transform_to_dataframe()` | Convertit les données en DataFrame propre |
| `write_to_supabase()` | Écrit dans Supabase sans doublons |
| `migrate_mongodb_to_supabase()` | Pipeline complet |

**Données collectées** :
- Latitude et Longitude de l'ISS
- Timestamp (Unix, converti en datetime)
- Identifiant MongoDB (mongo_id) pour traçabilité

---

### `Test_perf.py`
**Objectif** : Benchmark et comparaison des performances

```bash
python Test_perf.py
```

**6 Tests effectués** :

#### TEST 1: SELECT Simple
- Récupère tous les documents/lignes
- Mesure le temps baseline

#### TEST 2: SELECT avec Filtre
- Requête filtrée sur latitude > 0
- Comparaison des temps d'exécution

#### TEST 3: Agrégation
- COUNT et AVG(latitude)
- Compare les capacités d'agrégation

#### TEST 4: Filtre Longitude (SANS INDEX)
- Baseline pour l'impact des index
- Filtre sur longitude > 30

#### TEST 5: Filtre Longitude (AVEC INDEX)
- Création automatique des index
- Mesure de l'amélioration apportée

#### TEST 6: Impact des INDEX
- Comparaison directe avant/après index
- Calcul du gain de performance

---

## 📊 Résultats Attendus

### Format de Sortie

```
======================================================================
STATISTIQUES DES BASES
======================================================================

📦 MONGODB:
  Collection: ISS_loc
  Nombre de documents: 200
  Taille moyenne d'un doc: 342 bytes
  Taille totale: 0.12 MB

📦 SUPABASE:
  Table: iss_data
  Nombre de lignes: 200
  Taille de la table: 48.00 kB

======================================================================
RÉSUMÉ COMPARATIF
======================================================================

              Test        MongoDB (ms)  Supabase (ms)  Ratio (M/S)   Gagnant
    SELECT Simple              5.32           2.15         2.47x    SUPABASE
 SELECT avec Filtre            3.21           1.89         1.70x    SUPABASE
      Agrégation              12.45          4.32          2.88x    SUPABASE
Filtre Longitude (SANS INDEX)  15.23         28.45         0.54x    MONGODB
Filtre Longitude (AVEC INDEX)   2.11          1.45         1.46x    SUPABASE
```

---

## 🔍 Fonctionnalités Clés

### MongoDB
- ✅ Création automatique de collections
- ✅ Gestion des index
- ✅ Agrégations ($group, $match)
- ✅ Stats de collections (size, avgObjSize)

### Supabase
- ✅ Gestion des tables avec UNIQUE constraints
- ✅ EXPLAIN ANALYZE pour l'optimisation
- ✅ Index automatiques
- ✅ Stats de tables (pg_size_pretty)

### Gestion des Doublons
- ✅ Vérification via `mongo_id`
- ✅ Pas de réécriture des entrées existantes
- ✅ Compteur de lignes skippées

---

## 🛠️ API et Fonctions

### Connexions

```python
# MongoDB
mongo_client = connect_mongodb()

# Supabase
supabase_conn = connect_supabase()
```

### Requêtes avec Mesure de Performance

```python
# MongoDB
result = query_mongodb_with_explain(client, {"field": {"$gt": value}})

# Supabase
result = query_supabase_with_explain(connection, "SELECT * FROM table WHERE field > 5")
```

### Index

```python
# Créer
create_mongodb_index(client, "iss_position.longitude")
create_supabase_index(connection, "longitude", "idx_longitude")

# Lister
list_mongodb_indexes(client)
list_supabase_indexes(connection)

# Supprimer
drop_mongodb_index(client, "index_name")
drop_supabase_index(connection, "index_name")
```

### Migration

```python
# Pipeline complet
migrate_mongodb_to_supabase()

# Ou étape par étape
documents = read_data_from_mongodb()
df = transform_to_dataframe(documents)
write_to_supabase(df)
```

---

## 💡 Interprétation des Résultats

### Quand MongoDB est plus rapide ?
- ✅ Queries sans index sur très grandes collections
- ✅ Documents profondément imbriqués
- ✅ Agrégations complexes avec multiples stages

### Quand Supabase/PostgreSQL est plus rapide ?
- ✅ Queries filtrées (avec index)
- ✅ JOINs de tables
- ✅ Transactions ACID
- ✅ Requêtes sur données normalisées

---

## 📈 Points d'Amélioration Possibles

- [ ] Tester avec des datasets plus volumineux (millions de documents)
- [ ] Ajouter des tests de JOINs pour Supabase
- [ ] Implémenter des stratégies de sharding MongoDB
- [ ] Analyser la consommation mémoire
- [ ] Tests de scalabilité horizontale
- [ ] Benchmark des écritures (INSERT) vs lectures (SELECT)

---

## 🐛 Troubleshooting

### Erreur: "Authentication failed" MongoDB
- Vérifier les identifiants dans `.env`
- Vérifier que l'IP est whitelistée dans MongoDB Atlas
- S'assurer que le mot de passe ne contient pas de caractères spéciaux non-encodés

### Erreur: "Connection refused" Supabase
- Vérifier la structure de l'URL PostgreSQL
- S'assurer que le port (généralement 6543 ou 5432) est accessible
- Vérifier les permissions de l'utilisateur PostgreSQL

### Erreur: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Erreur: "No module named 'pymongo'"
```bash
pip install pymongo
```

---

## 📚 Ressources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Documentation](https://supabase.com/docs/)
- [Open Notify ISS API](http://api.open-notify.org/)

---

## 👤 Auteur

- **Étudiant** : Sobmathias
- **Formation** : Master 1 - Performance des Bases de Données
- **Université** : [À compléter]
- **Date** : Janvier 2026

---

## 📄 License

Ce projet est fourni à titre éducatif.

---

## 🎓 Conclusion

Cette étude démontre que :

1. **PostgreSQL (Supabase)** excelle pour les requêtes filtrées avec index et les données structurées
2. **MongoDB** offre plus de flexibilité pour les documents complexes et imbriqués
3. **Les index sont cruciaux** pour les deux bases - L'impact peut être de 5-10x
4. **Le choix dépend** du use case : SQL pour données relationnelles, NoSQL pour données semi-structurées

---

**Dernière mise à jour** : 20 Janvier 2026
