CREATE TABLE IF NOT EXISTS tracks
(
    id String,
    title String,
    artist String,

    genre String,
    mood String,

    bpm UInt16,
    energy UInt8,
    duration_seconds UInt16,

    instrumentation String,

    sync_available Bool,
    commercial_use Bool,

    territory String,

    license_price Float64,
    license_type String
)
ENGINE = MergeTree
ORDER BY id;