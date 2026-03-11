-- Regions Table
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    region VARCHAR(50),
    UNIQUE(state)
);

-- Aggregated Transaction
CREATE TABLE IF NOT EXISTS aggregated_transaction (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    transaction_type VARCHAR(100),
    transaction_count BIGINT,
    transaction_amount NUMERIC(20,2),
    UNIQUE (state, year, quarter, transaction_type)
);

-- Aggregated Insurance
CREATE TABLE IF NOT EXISTS aggregated_insurance (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    transaction_type VARCHAR(100),
    transaction_count BIGINT,
    transaction_amount NUMERIC(20,2),
    UNIQUE (state, year, quarter, transaction_type)
);

-- Aggregated User
CREATE TABLE IF NOT EXISTS aggregated_user (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    brand VARCHAR(100),
    user_count BIGINT,
    percentage NUMERIC(10,6),
    UNIQUE (state, year, quarter, brand)
);

-- Map Transaction
CREATE TABLE IF NOT EXISTS map_transaction (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(150),
    count BIGINT,
    amount NUMERIC(20,2),
    UNIQUE (state, year, quarter, district)
);

-- Map Insurance
CREATE TABLE IF NOT EXISTS map_insurance (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(150),
    count BIGINT,
    amount NUMERIC(20,2),
    UNIQUE (state, year, quarter, district)
);

-- Map User
CREATE TABLE IF NOT EXISTS map_user (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(150),
    registered_users BIGINT,
    app_opens BIGINT,
    UNIQUE (state, year, quarter, district)
);

-- Top Transaction
CREATE TABLE IF NOT EXISTS top_transaction (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(150),
    count BIGINT,
    amount NUMERIC(20,2),
    UNIQUE (state, year, quarter, district)
);

-- Top Insurance
CREATE TABLE IF NOT EXISTS top_insurance (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    district VARCHAR(150),
    count BIGINT,
    amount NUMERIC(20,2),
    UNIQUE (state, year, quarter, district)
);

-- Top User
CREATE TABLE IF NOT EXISTS top_user (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100),
    year INT,
    quarter INT,
    pincode VARCHAR(20),
    registered_users BIGINT,
    UNIQUE (state, year, quarter, pincode)
);