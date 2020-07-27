CREATE DATABASE hacktj_live;
CREATE USER live_admin WITH PASSWORD '817m5da7fyleau^108yko2ib!&+*!0ba38gh%g8ps()56)=gsv';
ALTER ROLE live_admin SET client_encoding TO 'utf8';
ALTER ROLE live_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE live_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hacktj_live TO live_admin;
