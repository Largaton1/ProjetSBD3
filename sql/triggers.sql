-- Trigger de chiffrement
CREATE OR REPLACE FUNCTION encrypt_sal_trigger() RETURNS TRIGGER AS $$
BEGIN
  NEW.SAL := encrypt_salary(NEW.SAL::INT);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER   trg_encrypt_sal ON EMP;

CREATE TRIGGER trg_encrypt_sal
BEFORE INSERT OR UPDATE ON EMP
FOR EACH ROW
EXECUTE FUNCTION encrypt_sal_trigger();
