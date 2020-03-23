DROP DATABASE mes_db;

CREATE DATABASE mes_db
  WITH OWNER = rupasgon
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'C'
       LC_CTYPE = 'C'
       CONNECTION LIMIT = -1;