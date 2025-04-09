import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# 🔐 Paramètres de connexion PostgreSQL 
conn_params = {
    "dbname": "projet3",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}
# ✅ Vérifie la connexion une seule fois
def check_connection():
    try:
        conn = psycopg2.connect(**conn_params)
        conn.close()
        print("Connexion réussie à PostgreSQL\n")
    except Exception as e:
        print("Erreur de connexion :", e)
        exit()

# Génération des données simulées (N(5000, 500))
def generate_data(n=1000, seed=42):
    np.random.seed(seed)
    enames = [f"Employee_{i}" for i in range(1, n + 1)]
    jobs = np.random.choice(["Engineer", "Manager", "Analyst", "Clerk"], size=n)
    hire_dates = pd.to_datetime(np.random.randint(946684800, 1609459200, size=n), unit='s')
    salaries = np.random.normal(5000, 500, size=n).astype(int)
    return pd.DataFrame({
        "ENAME": enames,
        "JOB": jobs,
        "HIREDATE": hire_dates,
        "SAL": salaries
    })

# Insertion des données (déclenche le trigger de chiffrement)
def insert_data(conn, df):
    cur = conn.cursor()
    start = time.time()
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO EMP (ENAME, JOB, HIREDATE, SAL)
            VALUES (%s, %s, %s, %s)
        """, (row["ENAME"], row["JOB"], row["HIREDATE"].date(), int(row["SAL"])))
    conn.commit()
    cur.close()
    return time.time() - start

# 📤 Lecture via la vue EMP_DECRYPTED (déclenche déchiffrement)
def read_data(conn):
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT * FROM EMP_ENCRYPTED_DECRYPTED")

    _ = cur.fetchall()
    cur.close()
    return time.time() - start

# 🧪 Benchmark complet sur différentes tailles
def run_benchmark(sample_sizes):
    insert_times = []
    read_times = []

    for n in sample_sizes:
        print(f"🔍 Test avec {n} lignes...")
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("DELETE FROM EMP")  # Nettoie la table
        conn.commit()

        df = generate_data(n)
        t_insert = insert_data(conn, df)
        t_read = read_data(conn)

        insert_times.append(t_insert)
        read_times.append(t_read)

        conn.close()

    # Export CSV
    results_df = pd.DataFrame({
        "Taille": sample_sizes,
        "Temps Insertion (s)": insert_times,
        "Temps Lecture (s)": read_times
    })
    results_df.to_csv("resultats.csv", index=False, encoding="utf-8")
    print("Résultats exportés dans resultats.csv")

    return sample_sizes, insert_times, read_times

# 🚀 Lancement
if __name__ == "__main__":
    tailles = [100, 500, 1000, 5000, 10000]
    x, y_insert, y_read = run_benchmark(tailles)

    # Affichage console
    print("\n Résultats :")
    for i in range(len(x)):
        print(f"{x[i]} lignes → Insertion : {y_insert[i]:.2f}s | Lecture : {y_read[i]:.2f}s")

    # Graphique
    plt.plot(x, y_insert, label="Insertion (chiffrée)", marker='o')
    plt.plot(x, y_read, label="Lecture (vue déchiffrée)", marker='o')
    plt.xlabel("Nombre de lignes")
    plt.ylabel("Temps (secondes)")
    plt.title("Performance AES256-CBC selon le volume de données")
    plt.legend()
    plt.grid(True)
    plt.savefig("resultats_comparatifs.png")
    plt.show()
