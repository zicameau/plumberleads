-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- For geo-based queries

-- Create enum types if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'plumber');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_status') THEN
        CREATE TYPE lead_status AS ENUM ('new', 'matched', 'claimed', 'completed');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'claim_status') THEN
        CREATE TYPE claim_status AS ENUM ('new', 'contacted', 'completed', 'abandoned');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contact_status') THEN
        CREATE TYPE contact_status AS ENUM ('attempted', 'reached', 'no-answer', 'scheduled');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscription_status') THEN
        CREATE TYPE subscription_status AS ENUM ('inactive', 'active', 'past_due', 'canceled');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_type') THEN
        CREATE TYPE service_type AS ENUM (
            'emergency', 'leak', 'drain', 'toilet', 'faucet', 'sink', 'disposal', 
            'water_heater', 'sewer', 'repiping', 'gas_line', 'backflow', 'waterproofing',
            'sump_pump', 'commercial', 'inspection', 'maintenance', 'renovation', 'other'
        );
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'urgency_type') THEN
        CREATE TYPE urgency_type AS ENUM (
            'emergency', 'today', 'tomorrow', 'this_week', 'next_week', 'flexible'
        );
    END IF;
END$$;

-- Create local users table (without auth schema dependency)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'plumber',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create plumbers table with local reference
CREATE TABLE IF NOT EXISTS plumbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    service_radius INTEGER DEFAULT 25,
    services_offered service_type[] DEFAULT '{}',
    license_number TEXT,
    is_insured BOOLEAN DEFAULT FALSE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_status subscription_status DEFAULT 'inactive',
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    lead_credits INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT plumbers_email_unique UNIQUE (email)
);

-- Create spatial index for plumbers - FIXED SYNTAX
CREATE INDEX IF NOT EXISTS plumbers_location_idx ON plumbers USING GIST (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    problem_description TEXT,
    service_needed service_type[] NOT NULL,
    urgency urgency_type NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status lead_status DEFAULT 'new',
    reference_code TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create spatial index for leads - FIXED SYNTAX
CREATE INDEX IF NOT EXISTS leads_location_idx ON leads USING GIST (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

CREATE TABLE IF NOT EXISTS lead_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    plumber_id UUID NOT NULL REFERENCES plumbers(id) ON DELETE CASCADE,
    claimed_at TIMESTAMPTZ DEFAULT NOW(),
    status claim_status DEFAULT 'new',
    contact_status contact_status,
    notes TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT lead_claims_unique UNIQUE (lead_id, plumber_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS lead_claims_lead_idx ON lead_claims (lead_id);
CREATE INDEX IF NOT EXISTS lead_claims_plumber_idx ON lead_claims (plumber_id);

-- Create settings table for platform configuration
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Insert default settings
INSERT INTO settings (key, value, description)
VALUES
    ('lead_price', '10.00', 'Price per lead in USD'),
    ('lead_radius', '25', 'Default radius in miles for matching leads to plumbers'),
    ('monthly_subscription', '{"price": 49.99, "stripe_price_id": ""}', 'Monthly subscription details'),
    ('app_name', '"Plumber Leads"', 'Application name')
ON CONFLICT (key) DO NOTHING;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_plumbers_timestamp
BEFORE UPDATE ON plumbers
FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_leads_timestamp
BEFORE UPDATE ON leads
FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_lead_claims_timestamp
BEFORE UPDATE ON lead_claims
FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_settings_timestamp
BEFORE UPDATE ON settings
FOR EACH ROW EXECUTE PROCEDURE update_modified_column(); 