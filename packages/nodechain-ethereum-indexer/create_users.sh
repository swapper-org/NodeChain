#!/bin/bash
set -e

psql -U swapper swapper <<-EOSQL
    CREATE USER swapper_reader WITH PASSWORD 'swapper_reader';
    GRANT CONNECT ON DATABASE swapper TO swapper_reader;
    GRANT USAGE ON SCHEMA public TO swapper_reader;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO swapper_reader;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO swapper_reader;

    CREATE USER swapper_writer WITH PASSWORD 'swapper_writer';
    GRANT CONNECT ON DATABASE swapper TO swapper_writer;
    GRANT USAGE ON SCHEMA public TO swapper_writer;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO swapper_writer;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO swapper_writer;
EOSQL