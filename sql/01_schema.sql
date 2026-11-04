-- One row per person. Blood pressure is split into systolic and diastolic during cleaning.
DROP TABLE IF EXISTS people;

CREATE TABLE people (
    person_id          INTEGER PRIMARY KEY,
    gender             TEXT    NOT NULL CHECK (gender IN ('Male', 'Female')),
    age                INTEGER NOT NULL CHECK (age BETWEEN 18 AND 100),
    occupation         TEXT    NOT NULL,
    sleep_hours        REAL    NOT NULL CHECK (sleep_hours BETWEEN 0 AND 24),
    sleep_quality      INTEGER NOT NULL CHECK (sleep_quality BETWEEN 1 AND 10),
    activity_minutes   INTEGER NOT NULL CHECK (activity_minutes >= 0),
    stress_level       INTEGER NOT NULL CHECK (stress_level BETWEEN 1 AND 10),
    bmi_category       TEXT    NOT NULL CHECK (bmi_category IN ('Normal', 'Overweight', 'Obese')),
    bp_systolic        INTEGER NOT NULL,
    bp_diastolic       INTEGER NOT NULL,
    heart_rate         INTEGER NOT NULL,
    daily_steps        INTEGER NOT NULL,
    sleep_disorder     TEXT    NOT NULL CHECK (sleep_disorder IN ('None', 'Insomnia', 'Sleep Apnea')),
    profile_key        TEXT    NOT NULL       -- all fields except person_id, to find duplicate profiles
);
