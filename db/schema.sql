-- Plain PostgreSQL. Runs on any Postgres, including Tiger Data.
-- No table holds cell-level or building-level data. The smallest geometry is a neighborhood polygon.
-- The minimum count K is applied in pipeline/lib/suppression.py only. These checks guard the shape of
-- suppressed rows, and a test reads every stored row against K from config/city.yaml.

CREATE TABLE IF NOT EXISTS neighborhoods (
    neighborhood_id text PRIMARY KEY,
    name text NOT NULL,
    boundary_source text NOT NULL,
    coverage numeric(4, 3) NOT NULL CHECK (coverage > 0 AND coverage <= 1),
    geometry jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS neighborhood_year_exposure (
    neighborhood_id text NOT NULL REFERENCES neighborhoods (neighborhood_id),
    year_start date NOT NULL,
    return_period integer NOT NULL CHECK (return_period IN (10, 20, 50, 75, 100, 200, 500)),
    buildings_in_zone integer,
    new_buildings_in_zone integer,
    growth_pct numeric(8, 1),
    suppressed boolean NOT NULL,
    change_available boolean NOT NULL,
    PRIMARY KEY (neighborhood_id, return_period, year_start),
    CONSTRAINT suppressed_rows_hold_no_counts CHECK (
        NOT suppressed
        OR (buildings_in_zone IS NULL AND new_buildings_in_zone IS NULL AND growth_pct IS NULL)
    ),
    CONSTRAINT shown_rows_hold_a_count CHECK (suppressed OR buildings_in_zone IS NOT NULL),
    CONSTRAINT change_needs_a_baseline CHECK (
        change_available
        OR (new_buildings_in_zone IS NULL AND growth_pct IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS validation_result (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS briefs (
    neighborhood_id text NOT NULL REFERENCES neighborhoods (neighborhood_id),
    return_period integer NOT NULL,
    text text NOT NULL,
    source text NOT NULL CHECK (source IN ('gemini', 'template')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (neighborhood_id, return_period)
);
