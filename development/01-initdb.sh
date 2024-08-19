#!/bin/bash
set -e

# Create the guacamole_db database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE guacamole_db;
EOSQL
