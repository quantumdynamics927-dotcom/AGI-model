-- AGI-model Postgres bootstrap.
--
-- Mounted by docker-compose.yml into /docker-entrypoint-initdb.d/ so it
-- runs the first time the data volume is empty. Idempotent: safe to run
-- against an already-initialized cluster (the official postgres image
-- skips initdb if the volume already contains a cluster, so this file
-- only fires on a truly fresh volume).

-- The official postgres image creates POSTGRES_USER / POSTGRES_DB at
-- startup; we just need to grant the right privileges and make sure
-- the `tmtos` user owns the schema.

GRANT ALL PRIVILEGES ON DATABASE tmt_os TO tmtos;

-- Optional: a dedicated schema for calibration records. Uncomment to use.
-- CREATE SCHEMA IF NOT EXISTS calibration AUTHORIZATION tmtos;
-- GRANT ALL ON SCHEMA calibration TO tmtos;