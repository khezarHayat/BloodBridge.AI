-- ============================================================================
-- BloodBridge: Row Level Security Policies
-- Migration: 002_rls_policies.sql
-- Description: Comprehensive RLS policies for all tables
-- ============================================================================

-- ===========================================
-- HELPER FUNCTIONS FOR RLS
-- ===========================================

-- Get current user's role from trusted sources ONLY:
-- 1. Trusted app_metadata claim (which only service role / auth hooks can set, never user-editable)
-- 2. Database lookup from public.profiles (protected by RLS and cannot be escalated by users)
-- NEVER read user-editable user_metadata for authorization decisions.
CREATE OR REPLACE FUNCTION public.user_role()
RETURNS TEXT AS $$
DECLARE
  claim_role TEXT;
  profile_role TEXT;
BEGIN
  -- Check ONLY trusted app_metadata (never user_metadata)
  claim_role := (auth.jwt() -> 'app_metadata' ->> 'role');
  IF claim_role IS NOT NULL AND claim_role <> '' THEN
    RETURN claim_role;
  END IF;

  -- Fallback to database lookup with search_path secured
  SELECT role INTO profile_role FROM public.profiles WHERE id = auth.uid();
  RETURN profile_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE SET search_path = public;

-- Check if current user is admin
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (public.user_role() = 'admin');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE SET search_path = public;

-- Grant EXECUTE permissions to authenticated users and service role
GRANT EXECUTE ON FUNCTION public.user_role() TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated, service_role;



-- ===========================================
-- ENABLE RLS ON ALL TABLES
-- ===========================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE donors ENABLE ROW LEVEL SECURITY;
ALTER TABLE blood_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE blood_banks ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE donor_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE donation_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;


-- ===========================================
-- PROFILES POLICIES
-- ===========================================

-- Users can read their own profile, admins can read all, verified institutions are discoverable,
-- and matched parties with accepted invitations can view contact details.
DROP POLICY IF EXISTS "profiles_select" ON profiles;
CREATE POLICY "profiles_select"
  ON profiles FOR SELECT
  TO authenticated
  USING (
    -- User sees their own full profile
    id = auth.uid()
    -- Admins can view any profile
    OR public.is_admin()
    -- Verified institutional blood banks and hospitals are discoverable for coordination
    OR (role IN ('blood_bank', 'hospital') AND is_verified = true AND is_active = true)
    -- Donors and requesters connected via an accepted donation invitation can view each other
    OR EXISTS (
      SELECT 1 FROM donor_invitations di
      JOIN donors d ON d.id = di.donor_id
      JOIN blood_requests br ON br.id = di.request_id
      WHERE di.status = 'accepted'
        AND (
          (d.user_id = profiles.id AND br.requester_id = auth.uid())
          OR (br.requester_id = profiles.id AND d.user_id = auth.uid())
        )
    )
  );

-- Users can only update their own profile, and cannot escalate their role or self-verify
DROP POLICY IF EXISTS "profiles_update_own" ON profiles;
CREATE POLICY "profiles_update_own"
  ON profiles FOR UPDATE
  TO authenticated
  USING (id = auth.uid() OR public.is_admin())
  WITH CHECK (
    public.is_admin()
    OR (
      id = auth.uid()
      AND role = (SELECT p.role FROM public.profiles p WHERE p.id = auth.uid())
      AND is_verified = (SELECT p.is_verified FROM public.profiles p WHERE p.id = auth.uid())
    )
  );

-- Users can insert their own profile on signup (cannot self-assign admin role or self-verify)
DROP POLICY IF EXISTS "profiles_insert_own" ON profiles;
CREATE POLICY "profiles_insert_own"
  ON profiles FOR INSERT
  TO authenticated
  WITH CHECK (
    id = auth.uid()
    AND (
      public.is_admin()
      OR (role IN ('patient', 'donor', 'blood_bank', 'hospital') AND is_verified = false)
    )
  );

-- Admins can delete profiles
DROP POLICY IF EXISTS "profiles_delete_admin" ON profiles;
CREATE POLICY "profiles_delete_admin"
  ON profiles FOR DELETE
  TO authenticated
  USING (public.is_admin());


-- ===========================================
-- DONORS POLICIES
-- ===========================================

-- Public can read available and eligible donors (sensitive medical details protected via views/ownership)
DROP POLICY IF EXISTS "donors_select_public" ON donors;
CREATE POLICY "donors_select_public"
  ON donors FOR SELECT
  TO authenticated
  USING (
    -- Donors can see their own full record
    user_id = auth.uid()
    -- Others can see available + eligible donors
    OR (is_available = true AND is_eligible = true)
    -- Institutional healthcare facilities can view donor records
    OR public.user_role() IN ('blood_bank', 'hospital')
    -- Admins can see all
    OR public.is_admin()
  );

-- Donors can insert their own record on signup (cannot self-verify)
DROP POLICY IF EXISTS "donors_insert_own" ON donors;
CREATE POLICY "donors_insert_own"
  ON donors FOR INSERT
  TO authenticated
  WITH CHECK (
    user_id = auth.uid()
    AND (public.is_admin() OR (verified_at IS NULL AND verified_by IS NULL))
  );

-- Donors can update their own record, but cannot self-verify or alter eligibility
DROP POLICY IF EXISTS "donors_update_own" ON donors;
CREATE POLICY "donors_update_own"
  ON donors FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid() OR public.is_admin())
  WITH CHECK (
    public.is_admin()
    OR (
      user_id = auth.uid()
      AND is_eligible = (SELECT d.is_eligible FROM public.donors d WHERE d.id = donors.id)
      AND verified_at IS NOT DISTINCT FROM (SELECT d.verified_at FROM public.donors d WHERE d.id = donors.id)
      AND verified_by IS NOT DISTINCT FROM (SELECT d.verified_by FROM public.donors d WHERE d.id = donors.id)
    )
  );

-- Admins can delete donor records
DROP POLICY IF EXISTS "donors_delete_admin" ON donors;
CREATE POLICY "donors_delete_admin"
  ON donors FOR DELETE
  TO authenticated
  USING (public.is_admin());


-- ===========================================
-- BLOOD_REQUESTS POLICIES
-- ===========================================

-- Requesters can read their own requests; donors can read requests they're invited to; admins can read all
DROP POLICY IF EXISTS "blood_requests_select" ON blood_requests;
CREATE POLICY "blood_requests_select"
  ON blood_requests FOR SELECT
  TO authenticated
  USING (
    -- Requester can see their own
    requester_id = auth.uid()
    -- Donors can see requests they've been invited to
    OR EXISTS (
      SELECT 1 FROM donor_invitations di
      JOIN donors d ON d.id = di.donor_id
      WHERE di.request_id = blood_requests.id
        AND d.user_id = auth.uid()
    )
    -- Blood banks and hospitals can see pending/matching requests in their city
    OR (
      public.user_role() IN ('blood_bank', 'hospital')
      AND status IN ('pending', 'matching', 'matched')
    )
    -- Admins can see all
    OR public.is_admin()
  );

-- Authenticated users can create blood requests
DROP POLICY IF EXISTS "blood_requests_insert" ON blood_requests;
CREATE POLICY "blood_requests_insert"
  ON blood_requests FOR INSERT
  TO authenticated
  WITH CHECK (requester_id = auth.uid());

-- Requesters can update their own requests; admins can update all
DROP POLICY IF EXISTS "blood_requests_update" ON blood_requests;
CREATE POLICY "blood_requests_update"
  ON blood_requests FOR UPDATE
  TO authenticated
  USING (requester_id = auth.uid() OR public.is_admin())
  WITH CHECK (requester_id = auth.uid() OR public.is_admin());

-- Requesters can delete (cancel) their own; admins can delete all
DROP POLICY IF EXISTS "blood_requests_delete" ON blood_requests;
CREATE POLICY "blood_requests_delete"
  ON blood_requests FOR DELETE
  TO authenticated
  USING (requester_id = auth.uid() OR public.is_admin());


-- ===========================================
-- BLOOD_BANKS POLICIES
-- ===========================================

-- Public can read verified and active blood banks
DROP POLICY IF EXISTS "blood_banks_select" ON blood_banks;
CREATE POLICY "blood_banks_select"
  ON blood_banks FOR SELECT
  TO authenticated
  USING (
    -- Owner can see their own
    user_id = auth.uid()
    -- Public can see verified + active banks
    OR (is_verified = true AND is_active = true)
    -- Admins can see all
    OR public.is_admin()
  );

-- Blood bank owners can insert their own record (cannot self-verify)
DROP POLICY IF EXISTS "blood_banks_insert" ON blood_banks;
CREATE POLICY "blood_banks_insert"
  ON blood_banks FOR INSERT
  TO authenticated
  WITH CHECK (
    user_id = auth.uid()
    AND (public.is_admin() OR (is_verified = false AND verified_at IS NULL AND verified_by IS NULL))
  );

-- Owners can update their own; admins can update all (cannot self-verify)
DROP POLICY IF EXISTS "blood_banks_update" ON blood_banks;
CREATE POLICY "blood_banks_update"
  ON blood_banks FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid() OR public.is_admin())
  WITH CHECK (
    public.is_admin()
    OR (
      user_id = auth.uid()
      AND is_verified = (SELECT bb.is_verified FROM public.blood_banks bb WHERE bb.id = blood_banks.id)
      AND verified_at IS NOT DISTINCT FROM (SELECT bb.verified_at FROM public.blood_banks bb WHERE bb.id = blood_banks.id)
      AND verified_by IS NOT DISTINCT FROM (SELECT bb.verified_by FROM public.blood_banks bb WHERE bb.id = blood_banks.id)
    )
  );

-- Admins can delete blood banks
DROP POLICY IF EXISTS "blood_banks_delete" ON blood_banks;
CREATE POLICY "blood_banks_delete"
  ON blood_banks FOR DELETE
  TO authenticated
  USING (public.is_admin());


-- ===========================================
-- INVENTORY_BATCHES POLICIES
-- ===========================================

-- Public can read available inventory from verified banks; owners can read all their own
DROP POLICY IF EXISTS "inventory_select" ON inventory_batches;
CREATE POLICY "inventory_select"
  ON inventory_batches FOR SELECT
  TO authenticated
  USING (
    -- Bank owners can see all their batches
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = inventory_batches.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    -- Public can see available from verified banks
    OR (
      availability_status = 'available'
      AND screening_status = 'passed'
      AND EXISTS (
        SELECT 1 FROM blood_banks bb
        WHERE bb.id = inventory_batches.blood_bank_id
          AND bb.is_verified = true
          AND bb.is_active = true
      )
    )
    -- Admins can see all
    OR public.is_admin()
  );

-- Bank owners can insert batches for their bank
DROP POLICY IF EXISTS "inventory_insert" ON inventory_batches;
CREATE POLICY "inventory_insert"
  ON inventory_batches FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = inventory_batches.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  );

-- Bank owners can update their own batches
DROP POLICY IF EXISTS "inventory_update" ON inventory_batches;
CREATE POLICY "inventory_update"
  ON inventory_batches FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = inventory_batches.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = inventory_batches.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  );

-- Bank owners can delete their own batches
DROP POLICY IF EXISTS "inventory_delete" ON inventory_batches;
CREATE POLICY "inventory_delete"
  ON inventory_batches FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = inventory_batches.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  );


-- ===========================================
-- DONOR_INVITATIONS POLICIES
-- ===========================================

-- Donors can read their own invitations; requesters can read invitations for their requests
DROP POLICY IF EXISTS "invitations_select" ON donor_invitations;
CREATE POLICY "invitations_select"
  ON donor_invitations FOR SELECT
  TO authenticated
  USING (
    -- Donors can see their own invitations
    EXISTS (
      SELECT 1 FROM donors d
      WHERE d.id = donor_invitations.donor_id
        AND d.user_id = auth.uid()
    )
    -- Requesters can see invitations for their requests
    OR EXISTS (
      SELECT 1 FROM blood_requests br
      WHERE br.id = donor_invitations.request_id
        AND br.requester_id = auth.uid()
    )
    -- Admins can see all
    OR public.is_admin()
  );

-- System/admins/requesters can create invitations
DROP POLICY IF EXISTS "invitations_insert" ON donor_invitations;
CREATE POLICY "invitations_insert"
  ON donor_invitations FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM blood_requests br
      WHERE br.id = donor_invitations.request_id
        AND br.requester_id = auth.uid()
    )
    OR public.is_admin()
  );

-- Donors can update (respond to) their own invitations; requesters can cancel
DROP POLICY IF EXISTS "invitations_update" ON donor_invitations;
CREATE POLICY "invitations_update"
  ON donor_invitations FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM donors d
      WHERE d.id = donor_invitations.donor_id
        AND d.user_id = auth.uid()
    )
    OR EXISTS (
      SELECT 1 FROM blood_requests br
      WHERE br.id = donor_invitations.request_id
        AND br.requester_id = auth.uid()
    )
    OR public.is_admin()
  )
  WITH CHECK (
    public.is_admin()
    -- Donor responding to invitation (can only update response status)
    OR (
      EXISTS (
        SELECT 1 FROM donors d
        WHERE d.id = donor_invitations.donor_id
          AND d.user_id = auth.uid()
      )
      AND status IN ('accepted', 'declined')
    )
    -- Requester cancelling an invitation
    OR (
      EXISTS (
        SELECT 1 FROM blood_requests br
        WHERE br.id = donor_invitations.request_id
          AND br.requester_id = auth.uid()
      )
      AND status = 'cancelled'
    )
  );

-- Admins can delete invitations
DROP POLICY IF EXISTS "invitations_delete" ON donor_invitations;
CREATE POLICY "invitations_delete"
  ON donor_invitations FOR DELETE
  TO authenticated
  USING (public.is_admin());


-- ===========================================
-- DONATION_RECORDS POLICIES
-- ===========================================

-- Donors can see their own records; blood banks can see records at their bank; admins see all
DROP POLICY IF EXISTS "donation_records_select" ON donation_records;
CREATE POLICY "donation_records_select"
  ON donation_records FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM donors d
      WHERE d.id = donation_records.donor_id
        AND d.user_id = auth.uid()
    )
    OR EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = donation_records.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  );

-- Blood banks and admins can insert donation records
DROP POLICY IF EXISTS "donation_records_insert" ON donation_records;
CREATE POLICY "donation_records_insert"
  ON donation_records FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = donation_records.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  );

-- Blood banks and admins can update donation records
DROP POLICY IF EXISTS "donation_records_update" ON donation_records;
CREATE POLICY "donation_records_update"
  ON donation_records FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = donation_records.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM blood_banks bb
      WHERE bb.id = donation_records.blood_bank_id
        AND bb.user_id = auth.uid()
    )
    OR public.is_admin()
  );


-- ===========================================
-- NOTIFICATIONS POLICIES
-- ===========================================

-- Users can only read their own notifications
DROP POLICY IF EXISTS "notifications_select_own" ON notifications;
CREATE POLICY "notifications_select_own"
  ON notifications FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- Only admins can insert notifications directly from client; backend system notifications use service role
DROP POLICY IF EXISTS "notifications_insert_admin" ON notifications;
CREATE POLICY "notifications_insert_admin"
  ON notifications FOR INSERT
  TO authenticated
  WITH CHECK (public.is_admin());

-- Users can update (mark as read) their own notifications
DROP POLICY IF EXISTS "notifications_update_own" ON notifications;
CREATE POLICY "notifications_update_own"
  ON notifications FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Users can delete their own notifications
DROP POLICY IF EXISTS "notifications_delete_own" ON notifications;
CREATE POLICY "notifications_delete_own"
  ON notifications FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());


-- ===========================================
-- VERIFICATION_DOCUMENTS POLICIES
-- ===========================================

-- Users can see their own documents; admins can see all
DROP POLICY IF EXISTS "verification_docs_select" ON verification_documents;
CREATE POLICY "verification_docs_select"
  ON verification_documents FOR SELECT
  TO authenticated
  USING (user_id = auth.uid() OR public.is_admin());

-- Users can upload their own documents (must be submitted with pending status)
DROP POLICY IF EXISTS "verification_docs_insert" ON verification_documents;
CREATE POLICY "verification_docs_insert"
  ON verification_documents FOR INSERT
  TO authenticated
  WITH CHECK (
    user_id = auth.uid()
    AND (public.is_admin() OR status = 'pending')
  );

-- Admins can update (review) documents
DROP POLICY IF EXISTS "verification_docs_update" ON verification_documents;
CREATE POLICY "verification_docs_update"
  ON verification_documents FOR UPDATE
  TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- Users can delete their own pending documents; admins can delete any
DROP POLICY IF EXISTS "verification_docs_delete" ON verification_documents;
CREATE POLICY "verification_docs_delete"
  ON verification_documents FOR DELETE
  TO authenticated
  USING (
    (user_id = auth.uid() AND status = 'pending')
    OR public.is_admin()
  );


-- ===========================================
-- REQUEST_STATUS_HISTORY POLICIES
-- ===========================================

-- Requesters can see history for their requests; admins see all
DROP POLICY IF EXISTS "status_history_select" ON request_status_history;
CREATE POLICY "status_history_select"
  ON request_status_history FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM blood_requests br
      WHERE br.id = request_status_history.request_id
        AND br.requester_id = auth.uid()
    )
    OR public.is_admin()
  );

-- Requesters or admins can record status history
DROP POLICY IF EXISTS "status_history_insert" ON request_status_history;
CREATE POLICY "status_history_insert"
  ON request_status_history FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM blood_requests br
      WHERE br.id = request_status_history.request_id
        AND br.requester_id = auth.uid()
    )
    OR public.is_admin()
  );


-- ===========================================
-- AUDIT_LOGS POLICIES
-- ===========================================

-- Only admins can read audit logs
DROP POLICY IF EXISTS "audit_logs_select_admin" ON audit_logs;
CREATE POLICY "audit_logs_select_admin"
  ON audit_logs FOR SELECT
  TO authenticated
  USING (public.is_admin());

-- Only admins can manually insert audit logs; automated audits are recorded via backend service role (which bypasses RLS)
DROP POLICY IF EXISTS "audit_logs_insert_admin" ON audit_logs;
CREATE POLICY "audit_logs_insert_admin"
  ON audit_logs FOR INSERT
  TO authenticated
  WITH CHECK (public.is_admin());
