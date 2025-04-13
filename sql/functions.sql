-- 1. Activer pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. Supprimer les anciennes structures si elles existent
DROP VIEW IF EXISTS EMP_DECRYPTED;
DROP TABLE IF EXISTS EMP CASCADE;
DROP TABLE IF EXISTS crypto_keys CASCADE;

-- 3. Créer une table pour stocker la clé de chiffrement
-- Cette table contient la clé AES256 utilisée pour le chiffrement et le déchiffrement
-- des salaires dans la table EMP_ENCRYPTED.
-- La clé est stockée sous forme de texte.
-- La clé est générée aléatoirement et encodée en hexadécimal.

CREATE TABLE crypto_keys (
  id SERIAL PRIMARY KEY,
  key TEXT NOT NULL
);

-- 4. Insérer une clé AES256  dans la table crypto_keys
-- Cette clé est utilisée pour le chiffrement et le déchiffrement des salaires
-- dans la table EMP_ENCRYPTED.
-- La clé est générée aléatoirement et encodée en hexadécimal.
INSERT INTO crypto_keys (key)
VALUES (encode(gen_random_bytes(32), 'hex'));


-- 6. Fonction pour récupérer la clé (depuis la table)
CREATE OR REPLACE FUNCTION get_crypto_key() RETURNS TEXT AS $$
DECLARE
  k TEXT;
BEGIN
  SELECT key INTO k FROM crypto_keys ORDER BY id DESC LIMIT 1;
  RETURN k;
END;
$$ LANGUAGE plpgsql;

-- 7. Fonction de chiffrement du salaire
-- Cette fonction chiffre le salaire en utilisant la clé de la table crypto_keys
-- et retourne le résultat sous forme de BYTEA.
CREATE OR REPLACE FUNCTION encrypt_salary(salary INT) RETURNS BYTEA AS $$
DECLARE
  key TEXT := get_crypto_key();
BEGIN
  RETURN pgp_sym_encrypt(
    salary::TEXT,
    key,
    'cipher-algo=aes256, compress-algo=0'
  );
END;
$$ LANGUAGE plpgsql;

-- 8. Fonction de déchiffrement du salaire
CREATE OR REPLACE FUNCTION decrypt_salary(salary BYTEA) RETURNS INT AS $$
DECLARE
  key TEXT := get_crypto_key();
  decrypted TEXT;
BEGIN
  decrypted := pgp_sym_decrypt(salary, key);
  RETURN decrypted::INT;
END;
$$ LANGUAGE plpgsql;

-- Trigger AFTER INSERT sur EMP
-- Cette fonction est déclenchée après l'insertion d'une ligne dans la table EMP.
-- Elle insère une ligne dans la table EMP_ENCRYPTED avec le salaire chiffré.
-- La fonction utilise la fonction encrypt_salary pour chiffrer le salaire avant de l'insérer.
-- La table EMP_ENCRYPTED contient les colonnes EMPNO, ENAME, JOB, HIREDATE et SAL_ENC.
-- La colonne SAL_ENC contient le salaire chiffré.
CREATE OR REPLACE FUNCTION insert_into_encrypted() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO EMP_ENCRYPTED (EMPNO, ENAME, JOB, HIREDATE, SAL_ENC)
  VALUES (
    NEW.EMPNO,
    NEW.ENAME,
    NEW.JOB,
    NEW.HIREDATE,
    encrypt_salary(NEW.SAL)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- Verification de la fonction de chiffrement
CREATE TRIGGER trg_encrypt_on_insert
AFTER INSERT ON EMP
FOR EACH ROW
EXECUTE FUNCTION insert_into_encrypted();


-- Vue déchiffrée : EMP_ENCRYPTED_DECRYPTED
-- Cette vue déchiffre le salaire de la table EMP_ENCRYPTED
-- en utilisant la fonction decrypt_salary.

CREATE OR REPLACE VIEW EMP_ENCRYPTED_DECRYPTED AS
SELECT
  EMPNO,
  ENAME,
  JOB,
  HIREDATE,
  decrypt_salary(SAL_ENC) AS SAL
FROM EMP_ENCRYPTED;

-- Fonction de chiffrement du salaire en mode ECB

CREATE OR REPLACE FUNCTION encrypt_ecb(salary INT) RETURNS BYTEA AS $$
DECLARE
  key TEXT := (SELECT key FROM crypto_keys ORDER BY id DESC LIMIT 1);
BEGIN
 
  RETURN pgp_sym_encrypt(
    salary::TEXT,
    key,
    'cipher-algo=aes256, compress-algo=0'
  );
END;
$$ LANGUAGE plpgsql;

