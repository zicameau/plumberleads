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

-- Create auth schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS auth;

-- Create auth.users table if it doesn't exist (mock of Supabase auth.users for local development)
CREATE TABLE IF NOT EXISTS auth.users (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    email text UNIQUE,
    encrypted_password text,
    role text DEFAULT 'customer',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Function to get authenticated user ID (mock of Supabase auth.uid() for local development)
CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid AS $$
BEGIN
    RETURN current_setting('auth.user_id', true)::uuid;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create plumbers table
CREATE TABLE IF NOT EXISTS plumbers (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id) NOT NULL UNIQUE,
    company_name text,
    contact_name text,
    phone text,
    email text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Set up RLS (Row Level Security) policies
ALTER TABLE plumbers ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own plumber profile" ON plumbers;
DROP POLICY IF EXISTS "Users can update their own plumber profile" ON plumbers;
DROP POLICY IF EXISTS "Plumbers can insert their profile" ON plumbers;

-- Create new policies
CREATE POLICY "Users can view their own plumber profile"
    ON plumbers FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own plumber profile"
    ON plumbers FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Plumbers can insert their profile"
    ON plumbers FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_plumbers_updated_at ON plumbers;

CREATE TRIGGER update_plumbers_updated_at
    BEFORE UPDATE ON plumbers
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

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

CREATE TRIGGER update_users_timestamp
BEFORE UPDATE ON auth.users
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