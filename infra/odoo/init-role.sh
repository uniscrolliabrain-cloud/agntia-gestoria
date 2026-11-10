#!/usr/bin/env bash
# Sourced by the PostgreSQL entrypoint on a new volume.
psql -X -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<'SQL'
\getenv lab_password ODOO_LAB_DB_PASSWORD
CREATE ROLE agntia_lab LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'lab_password';
CREATE DATABASE agntia_test_a OWNER agntia_lab;
CREATE DATABASE agntia_test_b OWNER agntia_lab;
SQL
