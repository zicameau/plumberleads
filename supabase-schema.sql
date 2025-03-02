-- supabase/migrations/20240301000000_initial_schema.sql

-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- For geo-based queries

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'plumber');
CREATE TYPE lead_status AS ENUM ('new', 'matched', 'claimed', 'completed');
CREATE TYPE claim_status AS ENUM ('new', 'contacted', 'completed', 'abandoned');
CREATE TYPE contact_status AS ENUM ('attempted', 'reached', 'no-answer', 'scheduled');
CREATE TYPE subscription_status AS ENUM ('inactive', 'active', 'past_due', 'canceled');
CREATE TYPE service_type AS ENUM (
    'emergency', 'leak', 'drain', 'toilet', 'faucet', 'sink', 'disposal', 
    'water_heater', 'sewer', 'repiping', 'gas_line', 'backflow', 'waterproofing',
    'sump_pump', 'commercial', 'inspection', 'maintenance', 'renovation', 'other'
);
CREATE TYPE urgency_type AS ENUM (
    'emergency', 'today', 'tomorrow', 'this_week', 'next_week', 'flexible'
);

-- Create tables
CREATE TABLE IF NOT EXISTS plumbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
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

-- Create spatial index for plumbers
CREATE INDEX plumbers_location_idx ON plumbers USING GIST (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
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

-- Create spatial index for leads
CREATE INDEX leads_location_idx ON leads USING GIST (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
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
CREATE INDEX lead_claims_lead_idx ON lead_claims (lead_id);
CREATE INDEX lead_claims_plumber_idx ON lead_claims (plumber_id);

-- Create settings table for platform configuration
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id)
);

-- Insert default settings
INSERT INTO settings (key, value, description) VALUES
    ('lead_price', '10.00', 'Price per lead in USD'),
    ('lead_radius', '25', 'Default radius in miles for matching leads to plumbers'),
    ('monthly_subscription', '{"price": 49.99, "stripe_price_id": ""}', 'Monthly subscription details'),
    ('app_name', '"Plumber Leads"', 'Application name');

-- Create function for finding plumbers by location and services
CREATE OR REPLACE FUNCTION find_plumbers_by_location(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    radius_miles INTEGER DEFAULT 50,
    services service_type[] DEFAULT NULL,
    limit_count INTEGER DEFAULT 50
)
RETURNS SETOF plumbers
LANGUAGE plpgsql
AS $$
BEGIN
    IF services IS NULL OR array_length(services, 1) IS NULL THEN
        -- Find plumbers without filtering by services
        RETURN QUERY
        SELECT p.*
        FROM plumbers p
        WHERE p.is_active = TRUE
        AND p.subscription_status = 'active'
        AND ST_DWithin(
            ST_SetSRID(ST_MakePoint(p.longitude, p.latitude), 4326)::geography,
            ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
            radius_miles * 1609.34  -- Convert miles to meters
        )
        ORDER BY 
            ST_Distance(
                ST_SetSRID(ST_MakePoint(p.longitude, p.latitude), 4326)::geography,
                ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography
            )
        LIMIT limit_count;
    ELSE
        -- Find plumbers with matching services
        RETURN QUERY
        SELECT p.*
        FROM plumbers p
        WHERE p.is_active = TRUE
        AND p.subscription_status = 'active'
        AND ST_DWithin(
            ST_SetSRID(ST_MakePoint(p.longitude, p.latitude), 4326)::geography,
            ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
            radius_miles * 1609.34  -- Convert miles to meters
        )
        AND p.services_offered && services  -- Check for any matching services
        ORDER BY 
            -- Rank plumbers with more matching services higher
            array_length(array(SELECT unnest(p.services_offered) INTERSECT SELECT unnest(services)), 1) DESC,
            ST_Distance(
                ST_SetSRID(ST_MakePoint(p.longitude, p.latitude), 4326)::geography,
                ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography
            )
        LIMIT limit_count;
    END IF;
END;
$$;

-- Create function for finding leads by location
CREATE OR REPLACE FUNCTION find_leads_by_location(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    radius_miles INTEGER DEFAULT 25,
    status lead_status DEFAULT 'new',
    limit_count INTEGER DEFAULT 20
)
RETURNS SETOF leads
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT l.*
    FROM leads l
    WHERE l.status = status
    AND ST_DWithin(
        ST_SetSRID(ST_MakePoint(l.longitude, l.latitude), 4326)::geography,
        ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
        radius_miles * 1609.34  -- Convert miles to meters
    )
    ORDER BY 
        ST_Distance(
            ST_SetSRID(ST_MakePoint(l.longitude, l.latitude), 4326)::geography,
            ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography
        )
    LIMIT limit_count;
END;
$$;

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

-- Set up Row Level Security policies
ALTER TABLE plumbers ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Create policies for plumbers table
CREATE POLICY "Plumbers can read their own profile"
ON plumbers FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Plumbers can update their own profile"
ON plumbers FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Admins can read all plumber profiles"
ON plumbers FOR SELECT
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));

CREATE POLICY "Admins can update all plumber profiles"
ON plumbers FOR UPDATE
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));

-- Create policies for leads table
CREATE POLICY "Anyone can create leads" 
ON leads FOR INSERT WITH CHECK (true);

CREATE POLICY "Plumbers can read leads they've claimed"
ON leads FOR SELECT
USING (EXISTS (
    SELECT 1 FROM lead_claims
    JOIN plumbers ON lead_claims.plumber_id = plumbers.id
    WHERE lead_claims.lead_id = leads.id
    AND plumbers.user_id = auth.uid()
));

CREATE POLICY "Admins can read all leads"
ON leads FOR SELECT
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));

CREATE POLICY "Admins can update all leads"
ON leads FOR UPDATE
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));

-- Create policies for lead_claims table
CREATE POLICY "Plumbers can create their own claims"
ON lead_claims FOR INSERT
WITH CHECK (EXISTS (
    SELECT 1 FROM plumbers
    WHERE plumbers.id = lead_claims.plumber_id
    AND plumbers.user_id = auth.uid()
));

CREATE POLICY "Plumbers can read their own claims"
ON lead_claims FOR SELECT
USING (EXISTS (
    SELECT 1 FROM plumbers
    WHERE plumbers.id = lead_claims.plumber_id
    AND plumbers.user_id = auth.uid()
));

CREATE POLICY "Plumbers can update their own claims"
ON lead_claims FOR UPDATE
USING (EXISTS (
    SELECT 1 FROM plumbers
    WHERE plumbers.id = lead_claims.plumber_id
    AND plumbers.user_id = auth.uid()
));

CREATE POLICY "Admins can read all claims"
ON lead_claims FOR SELECT
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));

CREATE POLICY "Admins can update all claims"
ON lead_claims FOR UPDATE
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));

-- Create policies for settings table
CREATE POLICY "Anyone can read settings"
ON settings FOR SELECT USING (true);

CREATE POLICY "Only admins can modify settings"
ON settings
USING (EXISTS (
    SELECT 1 FROM auth.users
    WHERE auth.users.id = auth.uid() 
    AND auth.users.raw_user_meta_data->>'role' = 'admin'
));
