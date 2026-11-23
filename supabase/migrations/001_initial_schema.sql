-- ============================================================================
-- BloodBridge: Initial Database Schema
-- Migration: 001_initial_schema.sql
-- Description: Creates all core tables, indexes, and trigger functions
-- ============================================================================

-- ===========================================
-- EXTENSIONS
-- ===========================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ===========================================
-- UTILITY FUNCTIONS
-- ===========================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Auto-generate request_number for blood_requests
CREATE OR REPLACE FUNCTION generate_request_number()
RETURNS TRIGGER AS $$
DECLARE
  next_num INTEGER;
  year_prefix TEXT;
BEGIN
  year_prefix := to_char(now(), 'YY');
  SELECT COALESCE(MAX(
    CAST(SUBSTRING(request_number FROM 'BR-[0-9]{2}([0-9]{4})') AS INTEGER)
  ), 0) + 1
  INTO next_num
  FROM blood_requests
  WHERE request_number LIKE 'BR-' || year_prefix || '%';

  NEW.request_number := 'BR-' || year_prefix || LPAD(next_num::TEXT, 4, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ===========================================
-- TABLE 1: profiles
-- ===========================================
CREATE TABLE IF NOT EXISTS profiles (
  id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email         TEXT NOT NULL,
  full_name     TEXT NOT NULL,
  phone         TEXT,
  role          TEXT NOT NULL CHECK (role IN ('patient', 'donor', 'blood_bank', 'hospital', 'admin')),
  avatar_url    TEXT,
  city          TEXT DEFAULT 'Peshawar',
  district      TEXT DEFAULT 'Peshawar',
  area          TEXT,
  address       TEXT,
  latitude      DOUBLE PRECISION,
  longitude     DOUBLE PRECISION,
  is_verified   BOOLEAN DEFAULT false,
  is_active     BOOLEAN DEFAULT true,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_profiles_updated_at ON profiles;
CREATE TRIGGER trg_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_city ON profiles(city);
CREATE INDEX IF NOT EXISTS idx_profiles_area ON profiles(area);
CREATE INDEX IF NOT EXISTS idx_profiles_is_active ON profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);


-- ===========================================
-- TABLE 2: donors
-- ===========================================
CREATE TABLE IF NOT EXISTS donors (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                 UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  blood_group             TEXT NOT NULL CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
  date_of_birth           DATE,
  gender                  TEXT CHECK (gender IN ('male','female','other')),
  weight                  NUMERIC,
  last_donation_date      DATE,
  total_donations         INTEGER DEFAULT 0,
  is_available            BOOLEAN DEFAULT true,
  availability_radius_km  NUMERIC DEFAULT 10,
  consent_notifications   BOOLEAN DEFAULT true,
  medical_conditions      TEXT,
  is_eligible             BOOLEAN DEFAULT true,
  verified_at             TIMESTAMPTZ,
  verified_by             UUID REFERENCES profiles(id),
  created_at              TIMESTAMPTZ DEFAULT now(),
  updated_at              TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id)
);

DROP TRIGGER IF EXISTS trg_donors_updated_at ON donors;
CREATE TRIGGER trg_donors_updated_at
  BEFORE UPDATE ON donors
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_donors_user_id ON donors(user_id);
CREATE INDEX IF NOT EXISTS idx_donors_blood_group ON donors(blood_group);
CREATE INDEX IF NOT EXISTS idx_donors_is_available ON donors(is_available);
CREATE INDEX IF NOT EXISTS idx_donors_is_eligible ON donors(is_eligible);
CREATE INDEX IF NOT EXISTS idx_donors_last_donation_date ON donors(last_donation_date);
CREATE INDEX IF NOT EXISTS idx_donors_blood_group_available ON donors(blood_group, is_available, is_eligible);


-- ===========================================
-- TABLE 3: blood_banks
-- ===========================================
CREATE TABLE IF NOT EXISTS blood_banks (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  license_number  TEXT,
  type            TEXT CHECK (type IN ('blood_bank','hospital','both')),
  phone           TEXT,
  email           TEXT,
  address         TEXT NOT NULL,
  city            TEXT DEFAULT 'Peshawar',
  area            TEXT,
  latitude        DOUBLE PRECISION,
  longitude       DOUBLE PRECISION,
  operating_hours TEXT,
  is_verified     BOOLEAN DEFAULT false,
  is_active       BOOLEAN DEFAULT true,
  verified_at     TIMESTAMPTZ,
  verified_by     UUID REFERENCES profiles(id),
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id)
);

DROP TRIGGER IF EXISTS trg_blood_banks_updated_at ON blood_banks;
CREATE TRIGGER trg_blood_banks_updated_at
  BEFORE UPDATE ON blood_banks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_blood_banks_user_id ON blood_banks(user_id);
CREATE INDEX IF NOT EXISTS idx_blood_banks_city ON blood_banks(city);
CREATE INDEX IF NOT EXISTS idx_blood_banks_is_verified ON blood_banks(is_verified);
CREATE INDEX IF NOT EXISTS idx_blood_banks_is_active ON blood_banks(is_active);
CREATE INDEX IF NOT EXISTS idx_blood_banks_type ON blood_banks(type);


-- ===========================================
-- TABLE 4: inventory_batches
-- ===========================================
CREATE TABLE IF NOT EXISTS inventory_batches (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  blood_bank_id       UUID NOT NULL REFERENCES blood_banks(id) ON DELETE CASCADE,
  blood_group         TEXT NOT NULL CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
  units_available     INTEGER NOT NULL CHECK (units_available >= 0),
  collection_date     DATE NOT NULL,
  expiry_date         DATE NOT NULL,
  screening_status    TEXT DEFAULT 'pending'
                        CHECK (screening_status IN ('pending','passed','failed')),
  availability_status TEXT DEFAULT 'available'
                        CHECK (availability_status IN ('available','reserved','used','expired','quarantined')),
  batch_number        TEXT,
  notes               TEXT,
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_inventory_batches_updated_at ON inventory_batches;
CREATE TRIGGER trg_inventory_batches_updated_at
  BEFORE UPDATE ON inventory_batches
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_inventory_blood_bank_id ON inventory_batches(blood_bank_id);
CREATE INDEX IF NOT EXISTS idx_inventory_blood_group ON inventory_batches(blood_group);
CREATE INDEX IF NOT EXISTS idx_inventory_availability ON inventory_batches(availability_status);
CREATE INDEX IF NOT EXISTS idx_inventory_expiry ON inventory_batches(expiry_date);
CREATE INDEX IF NOT EXISTS idx_inventory_screening ON inventory_batches(screening_status);
CREATE INDEX IF NOT EXISTS idx_inventory_bank_group_status ON inventory_batches(blood_bank_id, blood_group, availability_status);


-- ===========================================
-- TABLE 5: blood_requests
-- ===========================================
CREATE TABLE IF NOT EXISTS blood_requests (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_number      TEXT UNIQUE NOT NULL DEFAULT '',
  requester_id        UUID REFERENCES profiles(id),
  patient_name        TEXT NOT NULL,
  blood_group         TEXT NOT NULL CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
  units_needed        INTEGER NOT NULL CHECK (units_needed > 0),
  hospital_name       TEXT NOT NULL,
  hospital_address    TEXT,
  city                TEXT DEFAULT 'Peshawar',
  area                TEXT,
  latitude            DOUBLE PRECISION,
  longitude           DOUBLE PRECISION,
  emergency_level     TEXT NOT NULL CHECK (emergency_level IN ('critical','urgent','normal')),
  required_by         TIMESTAMPTZ,
  contact_name        TEXT NOT NULL,
  contact_phone       TEXT NOT NULL,
  additional_notes    TEXT,
  status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','matching','matched','donor_confirmed','fulfilled','cancelled','expired')),
  units_fulfilled     INTEGER DEFAULT 0,
  fulfilled_at        TIMESTAMPTZ,
  cancelled_at        TIMESTAMPTZ,
  cancellation_reason TEXT,
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_blood_requests_updated_at ON blood_requests;
CREATE TRIGGER trg_blood_requests_updated_at
  BEFORE UPDATE ON blood_requests
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_blood_requests_request_number ON blood_requests;
CREATE TRIGGER trg_blood_requests_request_number
  BEFORE INSERT ON blood_requests
  FOR EACH ROW EXECUTE FUNCTION generate_request_number();

CREATE INDEX IF NOT EXISTS idx_blood_requests_requester_id ON blood_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_blood_requests_status ON blood_requests(status);
CREATE INDEX IF NOT EXISTS idx_blood_requests_blood_group ON blood_requests(blood_group);
CREATE INDEX IF NOT EXISTS idx_blood_requests_emergency_level ON blood_requests(emergency_level);
CREATE INDEX IF NOT EXISTS idx_blood_requests_city ON blood_requests(city);
CREATE INDEX IF NOT EXISTS idx_blood_requests_created_at ON blood_requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blood_requests_status_emergency ON blood_requests(status, emergency_level);


-- ===========================================
-- TABLE 6: donor_invitations
-- ===========================================
CREATE TABLE IF NOT EXISTS donor_invitations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id      UUID NOT NULL REFERENCES blood_requests(id) ON DELETE CASCADE,
  donor_id        UUID NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
  status          TEXT DEFAULT 'pending'
                    CHECK (status IN ('pending','accepted','declined','expired','cancelled')),
  match_score     NUMERIC,
  match_reasons   JSONB,
  distance_km     NUMERIC,
  invited_at      TIMESTAMPTZ DEFAULT now(),
  responded_at    TIMESTAMPTZ,
  response_notes  TEXT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(request_id, donor_id)
);

CREATE INDEX IF NOT EXISTS idx_invitations_request_id ON donor_invitations(request_id);
CREATE INDEX IF NOT EXISTS idx_invitations_donor_id ON donor_invitations(donor_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON donor_invitations(status);


-- ===========================================
-- TABLE 7: donation_records
-- ===========================================
CREATE TABLE IF NOT EXISTS donation_records (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  donor_id        UUID REFERENCES donors(id),
  request_id      UUID REFERENCES blood_requests(id),
  blood_bank_id   UUID REFERENCES blood_banks(id),
  blood_group     TEXT NOT NULL CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
  units_donated   INTEGER DEFAULT 1,
  donation_date   DATE NOT NULL,
  status          TEXT DEFAULT 'completed'
                    CHECK (status IN ('scheduled','completed','cancelled','deferred')),
  notes           TEXT,
  verified_by     UUID REFERENCES profiles(id),
  created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_donations_donor_id ON donation_records(donor_id);
CREATE INDEX IF NOT EXISTS idx_donations_request_id ON donation_records(request_id);
CREATE INDEX IF NOT EXISTS idx_donations_blood_bank_id ON donation_records(blood_bank_id);
CREATE INDEX IF NOT EXISTS idx_donations_date ON donation_records(donation_date DESC);
CREATE INDEX IF NOT EXISTS idx_donations_status ON donation_records(status);


-- ===========================================
-- TABLE 8: notifications
-- ===========================================
CREATE TABLE IF NOT EXISTS notifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  message         TEXT NOT NULL,
  type            TEXT NOT NULL CHECK (type IN ('invitation','request_update','verification','system','reminder')),
  reference_type  TEXT,
  reference_id    UUID,
  is_read         BOOLEAN DEFAULT false,
  read_at         TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);


-- ===========================================
-- TABLE 9: verification_documents
-- ===========================================
CREATE TABLE IF NOT EXISTS verification_documents (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  document_type   TEXT NOT NULL,
  file_url        TEXT NOT NULL,
  status          TEXT DEFAULT 'pending'
                    CHECK (status IN ('pending','approved','rejected')),
  reviewed_by     UUID REFERENCES profiles(id),
  reviewed_at     TIMESTAMPTZ,
  review_notes    TEXT,
  created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_verification_user_id ON verification_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_verification_status ON verification_documents(status);


-- ===========================================
-- TABLE 10: request_status_history
-- ===========================================
CREATE TABLE IF NOT EXISTS request_status_history (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id  UUID NOT NULL REFERENCES blood_requests(id) ON DELETE CASCADE,
  old_status  TEXT,
  new_status  TEXT NOT NULL,
  changed_by  UUID REFERENCES profiles(id),
  notes       TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_status_history_request_id ON request_status_history(request_id);
CREATE INDEX IF NOT EXISTS idx_status_history_created_at ON request_status_history(created_at DESC);


-- ===========================================
-- TABLE 11: audit_logs
-- ===========================================
CREATE TABLE IF NOT EXISTS audit_logs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES profiles(id),
  action        TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id   UUID,
  details       JSONB,
  ip_address    TEXT,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_logs(created_at DESC);
