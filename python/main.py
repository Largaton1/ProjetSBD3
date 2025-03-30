import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Connexion PostgreSQL
conn_params = {
    "dbname": "projet3",
    "user": "miage",
    "password": "miage",
    "host": "localhost",
    "port": "5432"
}

# Génération des données (salaires ~ N(5000, 500))
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

# Insertion dans EMP (le trigger chiffre SAL)
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

# Lecture via la vue déchiffrée
def read_data(conn):
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT * FROM EMP_DECRYPTED")
    _ = cur.fetchall()
    cur.close()
    return time.time() - start

# Expérimentation complète
def run_experiment():
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("DELETE FROM EMP")  # Nettoie la table
    conn.commit()

    df = generate_data(1000)  # Tu peux changer le n
    t_insert = insert_data(conn, df)
    t_read = read_data(conn)

    conn.close()
    return t_insert, t_read

# Lancement
if __name__ == "__main__":
    insert_time, read_time = run_experiment()
    print(f"Insertion (chiffrée via trigger) : {insert_time:.2f} sec")
    print(f"Lecture (vue déchiffrée) : {read_time:.2f} sec")

    # Graphique
    plt.bar(["Insertion", "Lecture"], [insert_time, read_time])
    plt.ylabel("Temps (secondes)")
    plt.title("Performance AES256-CBC (1000 lignes)")
    plt.savefig("resultats.png")
    plt.show()
