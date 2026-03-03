CREATE TABLE IF NOT EXISTS sexes (
    sex_code INT PRIMARY KEY,
    sex_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
    region_code TEXT PRIMARY KEY,
    region_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ages (
    age_code TEXT PRIMARY KEY,
    age_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS measures (
    measure_code INT PRIMARY KEY,
    measure_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS causes (
    diagnosis_code TEXT PRIMARY KEY,
    diagnosis_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deaths (
    id SERIAL PRIMARY KEY,
    year INT NOT NULL,
    region_code TEXT NOT NULL REFERENCES regions(region_code),
    sex_code INT NOT NULL REFERENCES sexes(sex_code),
    age_code TEXT NOT NULL REFERENCES ages(age_code),
    diagnosis_code TEXT NOT NULL REFERENCES causes(diagnosis_code),
    measure_code INT NOT NULL REFERENCES measures(measure_code),
    value NUMERIC NULL
);
