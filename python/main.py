
import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Connexion PostgreSQL
conn_params = {
    "dbname": "projet3",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

# Génération des données
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

def insert_plain(conn, df):
    cur = conn.cursor()
    start = time.time()
    for _, row in df.iterrows():
        cur.execute("INSERT INTO EMP_PLAIN (ENAME, JOB, HIREDATE, SAL) VALUES (%s, %s, %s, %s)",
                    (row["ENAME"], row["JOB"], row["HIREDATE"].date(), int(row["SAL"])))
    conn.commit()
    cur.close()
    return time.time() - start

def insert_encrypted(conn, df):
    cur = conn.cursor()
    start = time.time()
    for _, row in df.iterrows():
        cur.execute("INSERT INTO EMP (ENAME, JOB, HIREDATE, SAL) VALUES (%s, %s, %s, %s)",
                    (row["ENAME"], row["JOB"], row["HIREDATE"].date(), int(row["SAL"])))
    conn.commit()
    cur.close()
    return time.time() - start

def read_plain(conn):
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT * FROM EMP_PLAIN")
    _ = cur.fetchall()
    cur.close()
    return time.time() - start

def read_encrypted(conn):
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT * FROM EMP_ENCRYPTED_DECRYPTED")
    _ = cur.fetchall()
    cur.close()
    return time.time() - start

def read_encrypted_raw(conn):
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT * FROM EMP_ENCRYPTED")
    _ = cur.fetchall()
    cur.close()
    return time.time() - start

def comparaison(sample_sizes):
    results = []

    with psycopg2.connect(**conn_params) as conn:
        cur = conn.cursor()
        for n in sample_sizes:
            print(f"Test avec {n} lignes...")

            cur.execute("DELETE FROM EMP")
            cur.execute("DELETE FROM EMP_ENCRYPTED")
            cur.execute("DELETE FROM EMP_PLAIN")
            conn.commit()

            df = generate_data(n)

            t_plain_insert = insert_plain(conn, df)
            t_enc_insert = insert_encrypted(conn, df)
            t_plain_read = read_plain(conn)
            t_enc_read = read_encrypted(conn)
            t_enc_raw_read = read_encrypted_raw(conn)

            results.append({
                "Taille": n,
                "Insertion en clair": t_plain_insert,
                "Insertion chiffrée": t_enc_insert,
                "Lecture en clair": t_plain_read,
                "Lecture chiffrée": t_enc_raw_read,
                "Lecture déchiffrée": t_enc_read
            })

    df_results = pd.DataFrame(results)
    csv_path = "D:/ProjetSBD3/resultats.csv"
    df_results.to_csv(csv_path, index=False)

    # Graphique Insertion claire vs chiffrée
    plt.figure()
    plt.plot(df_results["Taille"], df_results["Insertion en clair"], label="Insertion en clair", marker='o')
    plt.plot(df_results["Taille"], df_results["Insertion chiffrée"], label="Insertion chiffrée", marker='o')
    plt.xlabel("Nombre de lignes")
    plt.ylabel("Temps (secondes)")
    plt.title("Comparaison des insertions : clair vs chiffrée")
    plt.legend()
    plt.grid(True)
    plt.savefig("D:/ProjetSBD3/graphique_insertion.png")
    plt.close()

    # Graphique Lecture claire vs déchiffrée
    plt.figure()
    plt.plot(df_results["Taille"], df_results["Lecture en clair"], label="Lecture en clair", marker='o')
    plt.plot(df_results["Taille"], df_results["Lecture déchiffrée"], label="Lecture déchiffrée", marker='o')
    plt.xlabel("Nombre de lignes")
    plt.ylabel("Temps (secondes)")
    plt.title("Lecture : clair vs déchiffré")
    plt.legend()
    plt.grid(True)
    plt.savefig("D:/ProjetSBD3/graphique_lecture_clair_dechiffre.png")
    plt.close()

    # Graphique Lecture chiffrée vs déchiffrée
    plt.figure()
    plt.plot(df_results["Taille"], df_results["Lecture chiffrée"], label="Lecture chiffrée", marker='o')
    plt.plot(df_results["Taille"], df_results["Lecture déchiffrée"], label="Lecture déchiffrée", marker='o')
    plt.xlabel("Nombre de lignes")
    plt.ylabel("Temps (secondes)")
    plt.title("Lecture : chiffrée vs déchiffrée")
    plt.legend()
    plt.grid(True)
    plt.savefig("D:/ProjetSBD3/graphique_lecture_chiffre_dechiffre.png")
    plt.close()

    return csv_path

# Exécution
comparaison([100, 500, 1000, 5000])

