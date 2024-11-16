CREATE EXTENSION timescaledb;
CREATE EXTENSION postgis;

CREATE TABLE sensors_data (
    "time" timestamp with time zone DEFAULT now() NOT NULL,
    ptc integer,
    v12_battery_voltage double precision,
    odometer integer,
    battery_percentage integer,
    remains_mileage integer,
    ignition_status integer,
    outside_temp integer,
    central_locking_status integer,
    door_fl_status integer,
    door_fr_status integer,
    trunk_status integer,
    door_rr_status integer,
    door_rl_status integer,
    head_lights_status integer,
    ready_status integer,
    battery_temp integer,
    climate_air_circulation integer,
    coolant_temp integer,
    in_board_temp integer,
    climate_fan_direction integer,
    climate_target_temp integer,
    climate_fan_speed integer,
    climate_auto_status integer,
    climate_r_window_status integer,
    charging_status integer,
    climate_ac_status integer,
    climate_status integer,
    climate_f_window_status integer,
    immobiliser integer
);

SELECT create_hypertable('sensors_data', 'time');

CREATE TABLE position_data (
    "time" timestamp with time zone DEFAULT now() NOT NULL,
    location public.geometry(Point,4326),
    speed double precision,
    course double precision,
    height double precision,
    sats integer,
    hdop double precision
);

SELECT create_hypertable('position_data', 'time');

CREATE TABLE token_storage (
    id SERIAL PRIMARY KEY,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
