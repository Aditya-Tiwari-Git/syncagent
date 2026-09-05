# Catalog Seeding

The ClickHouse `tracks` table is the source of truth for catalog metadata. The seed script creates the table from [schema.sql](schema.sql), inserts 15 deterministic demo tracks, and optionally adds reproducible generated tracks.

## Safe usage

```powershell
python database/seed_catalog.py
python database/seed_catalog.py --count 200 --seed 42
```

The default preserves existing rows and skips IDs already present. It never truncates the table. To intentionally replace the catalog:

```powershell
python database/seed_catalog.py --clear --count 200 --seed 42
```

`--append` is available for explicit append intent:

```powershell
python database/seed_catalog.py --append --count 50 --seed 7
```

The script requires `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_DATABASE`, `CLICKHOUSE_USER`, and `CLICKHOUSE_PASSWORD` in `.env`. It does not print credentials.

## Deterministic cases

The `TRK-DEMO-*` records cover valid matches, over-budget matches, unavailable sync rights, unavailable commercial usage, territory mismatch, multiple rights failures, slow/fast/low/high energy, cinematic, ambient, orchestral, electronic, acoustic, jazz, romantic, suspense, dark, hopeful, happy, urban, and piano-led scenes.
