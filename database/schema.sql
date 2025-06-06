CREATE TABLE linky (
    east INTEGER,
    sinst INTEGER,
    timestamp TIMESTAMP(1) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE linky_archive (
    east INTEGER,
    timestamp TIMESTAMP(1) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE on_off (
    device VARCHAR(30),
    state boolean,
    timestamp TIMESTAMP(1) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pressure (
    pressure REAL,
    timestamp TIMESTAMP(1) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sonoff_snzb02p (
    device VARCHAR(30),
    humidity REAL,
    temperature REAL,
    timestamp TIMESTAMP(1) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
