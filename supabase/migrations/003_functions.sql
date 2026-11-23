-- ============================================================================
-- BloodBridge: PostgreSQL Functions
-- Migration: 003_functions.sql
-- Description: Utility functions for donor matching, distance, and analytics
-- ============================================================================


-- ===========================================
-- FUNCTION: calculate_distance
-- Haversine formula for distance between two coordinates (returns km)
-- ===========================================
CREATE OR REPLACE FUNCTION calculate_distance(
  lat1 DOUBLE PRECISION,
  lon1 DOUBLE PRECISION,
  lat2 DOUBLE PRECISION,
  lon2 DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION AS $$
DECLARE
  r DOUBLE PRECISION := 6371; -- Earth radius in km
  d_lat DOUBLE PRECISION;
  d_lon DOUBLE PRECISION;
  a DOUBLE PRECISION;
  c DOUBLE PRECISION;
BEGIN
  -- Handle NULL coordinates
  IF lat1 IS NULL OR lon1 IS NULL OR lat2 IS NULL OR lon2 IS NULL THEN
    RETURN NULL;
  END IF;

  d_lat := radians(lat2 - lat1);
  d_lon := radians(lon2 - lon1);

  a := sin(d_lat / 2) * sin(d_lat / 2)
     + cos(radians(lat1)) * cos(radians(lat2))
     * sin(d_lon / 2) * sin(d_lon / 2);

  c := 2 * atan2(sqrt(a), sqrt(1 - a));

  RETURN r * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- ===========================================
-- FUNCTION: get_compatible_donors
-- Returns compatible donors based on blood group compatibility rules
-- Blood group compatibility (who can DONATE to whom):
--   O- can donate to anyone (universal donor)
--   O+ can donate to A+, B+, AB+, O+
--   A- can donate to A+, A-, AB+, AB-
--   A+ can donate to A+, AB+
--   B- can donate to B+, B-, AB+, AB-
--   B+ can donate to B+, AB+
--   AB- can donate to AB+, AB-
--   AB+ can donate to AB+ only
-- ===========================================
CREATE OR REPLACE FUNCTION get_compatible_donors(
  p_blood_group TEXT,
  p_city TEXT DEFAULT 'Peshawar',
  p_area TEXT DEFAULT NULL
)
RETURNS TABLE (
  donor_id UUID,
  user_id UUID,
  full_name TEXT,
  blood_group TEXT,
  phone TEXT,
  city TEXT,
  area TEXT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  last_donation_date DATE,
  total_donations INTEGER,
  is_available BOOLEAN,
  availability_radius_km NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id AS donor_id,
    d.user_id,
    p.full_name,
    d.blood_group,
    p.phone,
    p.city,
    p.area,
    p.latitude,
    p.longitude,
    d.last_donation_date,
    d.total_donations,
    d.is_available,
    d.availability_radius_km
  FROM donors d
  JOIN profiles p ON p.id = d.user_id
  WHERE d.is_available = true
    AND d.is_eligible = true
    AND p.is_active = true
    -- Blood group compatibility: which donors CAN donate to the requested group
    AND d.blood_group IN (
      CASE p_blood_group
        WHEN 'AB+' THEN 'A+' END,
      CASE p_blood_group
        WHEN 'AB+' THEN 'A-'
        WHEN 'AB-' THEN 'A-' END,
      CASE p_blood_group
        WHEN 'AB+' THEN 'B+'  END,
      CASE p_blood_group
        WHEN 'AB+' THEN 'B-'
        WHEN 'AB-' THEN 'B-' END,
      CASE p_blood_group
        WHEN 'AB+' THEN 'AB+'
        WHEN 'AB-' THEN 'AB-' END,
      -- Same blood group always compatible
      p_blood_group,
      -- O- is universal donor
      'O-',
      -- O+ can donate to positive types
      CASE WHEN p_blood_group IN ('A+', 'B+', 'AB+', 'O+') THEN 'O+' END,
      -- A- can donate to A types and AB types
      CASE WHEN p_blood_group IN ('A+', 'A-', 'AB+', 'AB-') THEN 'A-' END,
      -- B- can donate to B types and AB types
      CASE WHEN p_blood_group IN ('B+', 'B-', 'AB+', 'AB-') THEN 'B-' END,
      -- AB- can donate to AB types
      CASE WHEN p_blood_group IN ('AB+', 'AB-') THEN 'AB-' END
    )
    -- Ensure at least 56 days since last donation (8 weeks)
    AND (d.last_donation_date IS NULL OR d.last_donation_date <= CURRENT_DATE - INTERVAL '56 days')
    -- City filter
    AND (p_city IS NULL OR p.city = p_city)
    -- Area filter (optional, narrows down)
    AND (p_area IS NULL OR p.area = p_area)
  ORDER BY
    -- Prioritize exact blood group match
    CASE WHEN d.blood_group = p_blood_group THEN 0 ELSE 1 END,
    -- Then by most recent activity / fewer donations (fresh donors)
    d.total_donations ASC,
    d.last_donation_date ASC NULLS FIRST;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;


-- ===========================================
-- FUNCTION: get_blood_request_stats
-- Aggregate stats for admin dashboard
-- ===========================================
CREATE OR REPLACE FUNCTION get_blood_request_stats()
RETURNS TABLE (
  total_requests BIGINT,
  pending_requests BIGINT,
  active_requests BIGINT,
  fulfilled_requests BIGINT,
  cancelled_requests BIGINT,
  expired_requests BIGINT,
  critical_requests BIGINT,
  urgent_requests BIGINT,
  total_donors BIGINT,
  available_donors BIGINT,
  total_blood_banks BIGINT,
  verified_blood_banks BIGINT,
  total_donations BIGINT,
  requests_today BIGINT,
  requests_this_week BIGINT,
  requests_this_month BIGINT,
  avg_fulfillment_hours NUMERIC,
  fulfillment_rate NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    -- Request counts
    (SELECT COUNT(*) FROM blood_requests)::BIGINT AS total_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE status = 'pending')::BIGINT AS pending_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE status IN ('matching', 'matched', 'donor_confirmed'))::BIGINT AS active_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE status = 'fulfilled')::BIGINT AS fulfilled_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE status = 'cancelled')::BIGINT AS cancelled_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE status = 'expired')::BIGINT AS expired_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE emergency_level = 'critical' AND status NOT IN ('fulfilled', 'cancelled', 'expired'))::BIGINT AS critical_requests,
    (SELECT COUNT(*) FROM blood_requests WHERE emergency_level = 'urgent' AND status NOT IN ('fulfilled', 'cancelled', 'expired'))::BIGINT AS urgent_requests,

    -- Donor counts
    (SELECT COUNT(*) FROM donors)::BIGINT AS total_donors,
    (SELECT COUNT(*) FROM donors WHERE is_available = true AND is_eligible = true)::BIGINT AS available_donors,

    -- Blood bank counts
    (SELECT COUNT(*) FROM blood_banks)::BIGINT AS total_blood_banks,
    (SELECT COUNT(*) FROM blood_banks WHERE is_verified = true)::BIGINT AS verified_blood_banks,

    -- Donation count
    (SELECT COUNT(*) FROM donation_records WHERE status = 'completed')::BIGINT AS total_donations,

    -- Time-based request counts
    (SELECT COUNT(*) FROM blood_requests WHERE created_at >= CURRENT_DATE)::BIGINT AS requests_today,
    (SELECT COUNT(*) FROM blood_requests WHERE created_at >= date_trunc('week', CURRENT_DATE))::BIGINT AS requests_this_week,
    (SELECT COUNT(*) FROM blood_requests WHERE created_at >= date_trunc('month', CURRENT_DATE))::BIGINT AS requests_this_month,

    -- Average fulfillment time (in hours) for fulfilled requests
    (SELECT COALESCE(
      ROUND(AVG(EXTRACT(EPOCH FROM (fulfilled_at - created_at)) / 3600)::NUMERIC, 1),
      0
    ) FROM blood_requests WHERE status = 'fulfilled' AND fulfilled_at IS NOT NULL
    )::NUMERIC AS avg_fulfillment_hours,

    -- Fulfillment rate (percentage)
    (SELECT COALESCE(
      ROUND(
        COUNT(*) FILTER (WHERE status = 'fulfilled')::NUMERIC
        / NULLIF(COUNT(*) FILTER (WHERE status IN ('fulfilled', 'cancelled', 'expired')), 0)
        * 100, 1
      ),
      0
    ) FROM blood_requests
    )::NUMERIC AS fulfillment_rate;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;


-- ===========================================
-- FUNCTION: get_inventory_summary
-- Inventory summary by blood group for a blood bank
-- ===========================================
CREATE OR REPLACE FUNCTION get_inventory_summary(p_bank_id UUID)
RETURNS TABLE (
  blood_group TEXT,
  total_units BIGINT,
  available_units BIGINT,
  reserved_units BIGINT,
  expired_units BIGINT,
  quarantined_units BIGINT,
  earliest_expiry DATE,
  latest_collection DATE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    ib.blood_group,
    COALESCE(SUM(ib.units_available), 0)::BIGINT AS total_units,
    COALESCE(SUM(ib.units_available) FILTER (
      WHERE ib.availability_status = 'available' AND ib.screening_status = 'passed'
    ), 0)::BIGINT AS available_units,
    COALESCE(SUM(ib.units_available) FILTER (
      WHERE ib.availability_status = 'reserved'
    ), 0)::BIGINT AS reserved_units,
    COALESCE(SUM(ib.units_available) FILTER (
      WHERE ib.availability_status = 'expired' OR ib.expiry_date < CURRENT_DATE
    ), 0)::BIGINT AS expired_units,
    COALESCE(SUM(ib.units_available) FILTER (
      WHERE ib.availability_status = 'quarantined'
    ), 0)::BIGINT AS quarantined_units,
    MIN(ib.expiry_date) FILTER (
      WHERE ib.availability_status = 'available' AND ib.expiry_date >= CURRENT_DATE
    ) AS earliest_expiry,
    MAX(ib.collection_date) AS latest_collection
  FROM inventory_batches ib
  WHERE ib.blood_bank_id = p_bank_id
  GROUP BY ib.blood_group
  ORDER BY ib.blood_group;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;


-- ===========================================
-- FUNCTION: handle_new_user
-- Automatically create a profile when a new auth user signs up
-- Security constraints:
-- 1. Never trusts raw_user_meta_data for authorization roles (defaults to 'patient').
-- 2. Only trusted app_metadata (server/admin set) can assign non-default roles.
-- 3. Uses ON CONFLICT (id) DO NOTHING to prevent duplicate key errors with server registration.
-- ===========================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  trusted_role TEXT;
BEGIN
  -- Only read role from trusted raw_app_meta_data (never user-editable raw_user_meta_data)
  trusted_role := COALESCE(NEW.raw_app_meta_data->>'role', 'patient');

  -- Strict validation: only allowed roles, otherwise safe fallback to 'patient'
  IF trusted_role NOT IN ('patient', 'donor', 'blood_bank', 'hospital', 'admin') THEN
    trusted_role := 'patient';
  END IF;

  -- Create minimal base profile with safe default role and ON CONFLICT handling
  INSERT INTO public.profiles (id, email, full_name, role, is_verified, is_active)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
    trusted_role,
    false,
    true
  )
  ON CONFLICT (id) DO NOTHING;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Trigger on auth.users to auto-create profile
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
