-- ============================================================================
-- KisanDirect - PostgreSQL Schema (with PostGIS for location queries)
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- USERS & ROLES
-- ---------------------------------------------------------------------------
CREATE TYPE user_role AS ENUM ('FARMER', 'BUYER', 'ADMIN');

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    phone           VARCHAR(20) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            user_role NOT NULL,
    preferred_language VARCHAR(5) DEFAULT 'en',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- ---------------------------------------------------------------------------
-- FARMERS
-- ---------------------------------------------------------------------------
CREATE TABLE farmers (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    village             VARCHAR(150),
    district            VARCHAR(150),
    state               VARCHAR(150),
    land_size_acres     NUMERIC(6,2),
    location            GEOGRAPHY(POINT, 4326),   -- PostGIS point (lon, lat)
    reliability_score   NUMERIC(4,3) DEFAULT 0.80 CHECK (reliability_score BETWEEN 0 AND 1),
    created_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_farmers_location ON farmers USING GIST(location);

-- ---------------------------------------------------------------------------
-- BUYERS
-- ---------------------------------------------------------------------------
CREATE TYPE buyer_type AS ENUM ('RETAILER', 'RESTAURANT', 'FOOD_PROCESSOR', 'INSTITUTIONAL', 'FPO_AGGREGATOR');

CREATE TABLE buyers (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name       VARCHAR(200) NOT NULL,
    buyer_type          buyer_type NOT NULL,
    location            GEOGRAPHY(POINT, 4326),
    avg_monthly_volume_kg NUMERIC(10,2),
    created_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_buyers_location ON buyers USING GIST(location);

-- ---------------------------------------------------------------------------
-- CROPS (master list)
-- ---------------------------------------------------------------------------
CREATE TABLE crops (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    unit        VARCHAR(20) DEFAULT 'kg',
    category    VARCHAR(50)
);

-- ---------------------------------------------------------------------------
-- CROP LISTINGS
-- ---------------------------------------------------------------------------
CREATE TYPE listing_status AS ENUM ('ACTIVE', 'RESERVED', 'SOLD', 'EXPIRED', 'CANCELLED');
CREATE TYPE quality_grade AS ENUM ('Grade A', 'Grade B', 'Grade C');

CREATE TABLE crop_listings (
    id                      SERIAL PRIMARY KEY,
    farmer_id               INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    crop_id                 INTEGER NOT NULL REFERENCES crops(id),
    quantity_kg             NUMERIC(10,2) NOT NULL CHECK (quantity_kg > 0),
    quality_grade           quality_grade NOT NULL,
    expected_price_per_kg   NUMERIC(8,2) NOT NULL CHECK (expected_price_per_kg > 0),
    harvest_date            DATE NOT NULL,
    location                GEOGRAPHY(POINT, 4326),
    status                  listing_status DEFAULT 'ACTIVE',
    created_at              TIMESTAMPTZ DEFAULT now(),
    updated_at              TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_listings_crop ON crop_listings(crop_id);
CREATE INDEX idx_listings_status ON crop_listings(status);
CREATE INDEX idx_listings_location ON crop_listings USING GIST(location);

-- ---------------------------------------------------------------------------
-- OFFERS (buyer offers on a listing)
-- ---------------------------------------------------------------------------
CREATE TYPE offer_status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN');

CREATE TABLE offers (
    id                  SERIAL PRIMARY KEY,
    listing_id          INTEGER NOT NULL REFERENCES crop_listings(id) ON DELETE CASCADE,
    buyer_id            INTEGER NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    offered_price_per_kg NUMERIC(8,2) NOT NULL CHECK (offered_price_per_kg > 0),
    requested_quantity_kg NUMERIC(10,2) NOT NULL,
    needed_within_days  INTEGER DEFAULT 7,
    match_score         NUMERIC(5,2),          -- AI-computed at offer time
    match_explanation   JSONB,                 -- reasons[], sub_scores{}
    status              offer_status DEFAULT 'PENDING',
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_offers_listing ON offers(listing_id);
CREATE INDEX idx_offers_buyer ON offers(buyer_id);
CREATE INDEX idx_offers_status ON offers(status);

-- ---------------------------------------------------------------------------
-- ORDERS (created once an offer is accepted)
-- ---------------------------------------------------------------------------
CREATE TYPE order_status AS ENUM ('CREATED', 'CONFIRMED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED', 'DISPUTED');

CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    offer_id        INTEGER UNIQUE NOT NULL REFERENCES offers(id),
    listing_id      INTEGER NOT NULL REFERENCES crop_listings(id),
    farmer_id       INTEGER NOT NULL REFERENCES farmers(id),
    buyer_id        INTEGER NOT NULL REFERENCES buyers(id),
    final_price_per_kg NUMERIC(8,2) NOT NULL,
    final_quantity_kg  NUMERIC(10,2) NOT NULL,
    total_value     NUMERIC(12,2) GENERATED ALWAYS AS (final_price_per_kg * final_quantity_kg) STORED,
    status          order_status DEFAULT 'CREATED',
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_orders_farmer ON orders(farmer_id);
CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_status ON orders(status);

-- ---------------------------------------------------------------------------
-- PRICES (market price observations - can be real or synthetic, labeled)
-- ---------------------------------------------------------------------------
CREATE TABLE prices (
    id              SERIAL PRIMARY KEY,
    crop_id         INTEGER NOT NULL REFERENCES crops(id),
    market_name     VARCHAR(150),
    price_per_kg    NUMERIC(8,2) NOT NULL,
    observed_date   DATE NOT NULL,
    is_synthetic    BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_prices_crop_date ON prices(crop_id, observed_date);
CREATE INDEX idx_prices_recent_lookup ON prices(crop_id, observed_date DESC, price_per_kg);

-- ---------------------------------------------------------------------------
-- WAREHOUSES
-- ---------------------------------------------------------------------------
CREATE TABLE warehouses (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    location        GEOGRAPHY(POINT, 4326),
    capacity_kg     NUMERIC(12,2),
    operator_name   VARCHAR(150),
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- TRANSPORTERS
-- ---------------------------------------------------------------------------
CREATE TABLE transporters (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(150) NOT NULL,
    phone               VARCHAR(20),
    vehicle_type        VARCHAR(100),
    capacity_kg         NUMERIC(10,2),
    base_fare           NUMERIC(8,2),
    per_km_rate         NUMERIC(8,2),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- DELIVERIES
-- ---------------------------------------------------------------------------
CREATE TYPE delivery_status AS ENUM ('SCHEDULED', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'FAILED');

CREATE TABLE deliveries (
    id                      SERIAL PRIMARY KEY,
    order_id                INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    transporter_id          INTEGER REFERENCES transporters(id),
    distance_km             NUMERIC(8,2),
    estimated_cost          NUMERIC(10,2),
    estimated_delivery_hours NUMERIC(6,2),
    status                  delivery_status DEFAULT 'SCHEDULED',
    scheduled_at            TIMESTAMPTZ,
    delivered_at            TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_deliveries_order ON deliveries(order_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_deliveries_transporter_status ON deliveries(transporter_id, status);

-- ---------------------------------------------------------------------------
-- PAYMENTS / TRANSACTIONS
-- ---------------------------------------------------------------------------
CREATE TYPE payment_status AS ENUM ('PENDING', 'PAID', 'FAILED', 'REFUNDED');

CREATE TABLE payments (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    amount          NUMERIC(12,2) NOT NULL,
    status          payment_status DEFAULT 'PENDING',
    payment_method  VARCHAR(50),
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE transactions (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    payment_id      INTEGER REFERENCES payments(id),
    transaction_type VARCHAR(50) DEFAULT 'ORDER_PAYMENT',
    amount          NUMERIC(12,2) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_transactions_order ON transactions(order_id);

-- ---------------------------------------------------------------------------
-- REVIEWS
-- ---------------------------------------------------------------------------
CREATE TABLE reviews (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id),
    reviewer_user_id INTEGER NOT NULL REFERENCES users(id),
    rating          SMALLINT CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- NOTIFICATIONS
-- ---------------------------------------------------------------------------
CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(200),
    message         TEXT,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- Speeds up the most common marketplace dashboard and price-demand queries.
CREATE INDEX idx_listings_marketplace ON crop_listings(crop_id, status, harvest_date);
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);
CREATE INDEX idx_offers_listing_status_created ON offers(listing_id, status, created_at DESC);

-- ---------------------------------------------------------------------------
-- Trigger: keep updated_at fresh
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_listings_updated BEFORE UPDATE ON crop_listings FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_offers_updated BEFORE UPDATE ON offers FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_orders_updated BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();
