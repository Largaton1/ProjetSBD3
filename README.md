## Projet 3 - DBMS over Encrypted Data
# Overall objective
The goal is to protect sensitive data stored in a PostgreSQL database, specifically the salary column (SAL), by encrypting this data at rest (at-rest encryption). You must:
1. Set up automatic encryption/decryption in PostgreSQL using triggers.
2. Measure the performance (insert/read time) of this encryption with a Python script.
3. (Bonus) Attack the encryption using frequency analysis in ECB mode.
# Technical Environment
DBMS Used: PostgreSQL
Extension: pgcrypto (provides functions such as pgp_sym_encrypt, pgp_sym_decrypt)
SQL + PL/pgSQL Language: for the database, functions, and triggers
Python: for generating data and measuring performance
Encryption Algorithm: AES256 in CBC mode (required), ECB (optional for attacks)
