
# 📄 Projet 3 - DBMS over Encrypted Data

## 🎯 Objectif du projet
Le but de ce projet est de sécuriser les données sensibles, en particulier les salaires des employés, stockées dans une base PostgreSQL, via l'implémentation d'un chiffrement AES256 en mode CBC.
Nous avons également évalué l'impact du chiffrement sur les performances d'insertion et de lecture.

## 👨‍💻 Auteurs
- KONE Cyril
- NASSARA Loïc

## ⚙️ Prérequis
- PostgreSQL 13+
- Python 3.8+
- Extension PostgreSQL `pgcrypto`

Installer les modules Python nécessaires :

```bash
pip install psycopg2 pandas matplotlib
```

## 🛠️ Mise en place de la base de données

### 1. Créer la base de données
```sql
CREATE DATABASE projet3;
```

### 2. Activer l'extension pgcrypto
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### 3. Exécuter les scripts SQL
- `sql/creer_table.sql`
- `sql/functions.sql`


## 📐 Architecture du projet

| Composant | Description |
|:---------|:------------|
| EMP_PLAIN | Table contenant les salaires en clair |
| EMP | Table avec trigger de chiffrement automatique |
| EMP_ENCRYPTED | Stockage des salaires chiffrés |
| EMP_ENCRYPTED_DECRYPTED | Vue SQL pour lecture déchiffrée des salaires |

## 🚀 Lancement des tests de performance
Dans `/python/` :

```bash
python main.py
```

## ⚠️ Modifications à prévoir
- Mettre à jour les paramètres de connexion PostgreSQL dans `main.py`
- Adapter les chemins pour l'enregistrement des graphes PNG

## 📈 Résultats générés
- Fichiers CSV des temps mesurés
- Graphiques PNG de comparaison des performances
