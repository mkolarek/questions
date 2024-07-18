#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER wiki WITH PASSWORD 'wiki';
	CREATE DATABASE wiki;
	GRANT ALL PRIVILEGES ON DATABASE wiki TO wiki;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "wiki" <<-EOSQL
	CREATE SCHEMA wiki;
	GRANT ALL PRIVILEGES ON SCHEMA wiki TO wiki;
EOSQL
