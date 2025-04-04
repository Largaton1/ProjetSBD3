-- 1. Activer pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. Supprimer les anciennes structures si elles existent
DROP VIEW IF EXISTS EMP_DECRYPTED;
DROP TABLE IF EXISTS EMP CASCADE;
DROP TABLE IF EXISTS crypto_keys CASCADE;

-- 3. Créer une table pour stocker la clé de chiffrement
CREATE TABLE crypto_keys (
  id SERIAL PRIMARY KEY,
  key TEXT NOT NULL
);

-- 4. Insérer une clé AES256 (32 octets hexadécimaux → 64 caractères)
INSERT INTO crypto_keys (key)
VALUES (encode(gen_random_bytes(32), 'hex'));

-- 5. Créer la table EMP avec SAL en clair et SAL_ENC pour stockage chiffré
CREATE TABLE EMP (
  EMPNO SERIAL PRIMARY KEY,
  ENAME VARCHAR(256),
  JOB VARCHAR(256),
  HIREDATE DATE,
  SAL INT,
  SAL_ENC BYTEA
);

-- 6. Fonction pour récupérer la clé (depuis la table)
CREATE OR REPLACE FUNCTION get_crypto_key() RETURNS TEXT AS $$
DECLARE
  k TEXT;
BEGIN
  SELECT key INTO k FROM crypto_keys ORDER BY id DESC LIMIT 1;
  RETURN k;
END;
$$ LANGUAGE plpgsql;

-- 7. Fonction de chiffrement
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

-- 8. Fonction de déchiffrement
CREATE OR REPLACE FUNCTION decrypt_salary(salary BYTEA) RETURNS INT AS $$
DECLARE
  key TEXT := get_crypto_key();
  decrypted TEXT;
BEGIN
  decrypted := pgp_sym_decrypt(salary, key);
  RETURN decrypted::INT;
END;
$$ LANGUAGE plpgsql;

-- 9. Fonction de trigger
CREATE OR REPLACE FUNCTION encrypt_sal_trigger() RETURNS TRIGGER AS $$
BEGIN
  NEW.SAL_ENC := encrypt_salary(NEW.SAL);
  NEW.SAL := NULL;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 10. Déclencheur (trigger) sur la table EMP
CREATE TRIGGER trg_encrypt_sal
BEFORE INSERT OR UPDATE ON EMP
FOR EACH ROW
EXECUTE FUNCTION encrypt_sal_trigger();

-- 11. Vue pour afficher les salaires en clair
CREATE OR REPLACE VIEW EMP_DECRYPTED AS
SELECT
  EMPNO,
  ENAME,
  JOB,
  HIREDATE,
  decrypt_salary(SAL_ENC) AS SAL
FROM EMP;
