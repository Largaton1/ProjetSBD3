-- Initialiser la clé de chiffrement si elle n'existe pas
DO $$
BEGIN
  BEGIN
    -- Vérifie si la clé de chiffrement existe
    PERFORM current_setting('my.crypto_key');
    EXCEPTION WHEN OTHERS THEN
    -- Initialise la clé de chiffrement si elle n'existe pas
    PERFORM set_config('my.crypto_key', encode(gen_random_bytes(32), 'hex'), true);
  END;
END
$$;

-- Fonction de chiffrement
CREATE OR REPLACE FUNCTION encrypt_salary(salary INT) RETURNS BYTEA AS $$
DECLARE
  crypto_key BYTEA := decode(current_setting('my.crypto_key', true), 'hex');
  iv BYTEA := gen_random_bytes(16);
BEGIN
  RETURN pgp_sym_encrypt(
    salary::TEXT, 
    crypto_key, 
    'cipher-algo=aes256, compress-algo=0, mode=cipher-cbc, iv=' || encode(iv, 'hex')
  );
END;
$$ LANGUAGE plpgsql;

-- Fonction de déchiffrement
CREATE OR REPLACE FUNCTION decrypt_salary(salary BYTEA) RETURNS INT AS $$
DECLARE
  crypto_key BYTEA := decode(current_setting('my.crypto_key', true), 'hex');
  decrypted TEXT;
BEGIN
  decrypted := pgp_sym_decrypt(salary, crypto_key);
  RETURN decrypted::INT;
END;
$$ LANGUAGE plpgsql;