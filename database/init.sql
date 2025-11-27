-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create tables
CREATE TABLE IF NOT EXISTS river_gauges (
    id SERIAL PRIMARY KEY,
    usgs_site_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    elevation_ft FLOAT,
    drainage_area_sqmi FLOAT,
    current_flow_cfs FLOAT,
    current_guage_height_ft FLOAT,
    current_stage VARCHAR(20),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action_stage_ft FLOAT,
    flood_stage_ft FLOAT,
    major_flood_stage_ft FLOAT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gauge_measurements (
    id SERIAL PRIMARY KEY,
    gauge_id INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    flow_cfs FLOAT,
    gauge_height_ft FLOAT,
    precipitation_in FLOAT,
    temperature_f FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flood_predictions (
    id SERIAL PRIMARY KEY,
    prediction_time TIMESTAMPTZ NOT NULL,
    valid_time TIMESTAMPTZ NOT NULL,
    risk_level VARCHAR(20),
    risk_score FLOAT,
    confidence FLOAT,
    risk_area GEOMETRY(POLYGON, 4326),
    affected_gauges JSON,
    rainfall_forecast_in FLOAT,
    soil_saturation_pct FLOAT,
    upstream_flow_cfs FLOAT,
    model_version VARCHAR(20),
    processing_time_ms FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_zones (
    id SERIAL PRIMARY KEY,
    zone_name VARCHAR(100) NOT NULL,
    geometry GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    base_risk_level VARCHAR(20),
    population_estimation INTEGER,
    critical_infrastructure JSON,
    elevation_avg_ft FLOAT,
    elevation_min_ft FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_gauges_location ON river_gauges USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_measurements_timestamp ON gauge_measurements(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_time ON flood_predictions(prediction_time DESC);
CREATE INDEX IF NOT EXISTS idx_prediction_area ON flood_predictions USING GIST(risk_area);
CREATE INDEX IF NOT EXISTS idx_zone_geometry ON risk_zones USING GIST(geometry);

-- Create partitioning for measurements (by month)
-- Note: To use partitioning effectively, the original table creation usually needs to specify PARTITION BY.
-- Since we are using a simple CREATE TABLE above, we'll skip complex partitioning for now to avoid conflicts 
-- or we would need to recreate the table as partitioned. 
-- For this fix, I will comment out the template creation as it was failing and likely incorrect for the simple setup.
-- CREATE TABLE IF NOT EXISTS guage_measurements_template (
--     LIKE guage_measurements INCLUDING ALL
-- ) PARTITION BY RANGE (timestamp);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USER};