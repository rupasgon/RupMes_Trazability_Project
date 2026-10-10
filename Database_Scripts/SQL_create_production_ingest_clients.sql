CREATE TABLE IF NOT EXISTS public.production_ingest_clients (
    id BIGSERIAL PRIMARY KEY,
    client_id VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(200) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    plant_code VARCHAR(50),
    line_code VARCHAR(50),
    station_code VARCHAR(50),
    machine_code VARCHAR(50),
    source_system VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_production_ingest_clients_client_id_not_blank
        CHECK (trim(client_id) <> ''),
    CONSTRAINT ck_production_ingest_clients_description_not_blank
        CHECK (trim(description) <> '')
);

CREATE INDEX IF NOT EXISTS ix_production_ingest_clients_client_id
    ON public.production_ingest_clients (client_id);

CREATE INDEX IF NOT EXISTS ix_production_ingest_clients_active
    ON public.production_ingest_clients (is_active);
