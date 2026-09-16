#!/bin/bash
set -e

# This runs automatically the FIRST time the postgres container starts
# (postgres only executes /docker-entrypoint-initdb.d scripts on an empty data volume).
# It creates a second database for Airflow's metadata, separate from the project's data.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE airflow;
    GRANT ALL PRIVILEGES ON DATABASE airflow TO "$POSTGRES_USER";

    -- Create the two schemas for the project database (staging/core architecture)
    \connect "$POSTGRES_DB"
    CREATE SCHEMA IF NOT EXISTS staging;
    CREATE SCHEMA IF NOT EXISTS core;
EOSQL
