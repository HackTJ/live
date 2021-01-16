\set user_password `awk -F "\'" '/POSTGRES_PASSWORD/ { print $2; }' .env.local`

CREATE DATABASE hacktj_live;
CREATE USER live_postgres WITH PASSWORD :'user_password';
ALTER ROLE live_postgres SET client_encoding TO 'utf8';
ALTER ROLE live_postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE live_postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hacktj_live TO live_postgres;
