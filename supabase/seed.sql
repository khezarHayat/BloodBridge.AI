-- ============================================================================
-- BloodBridge: Demo Seed Data
-- File: seed.sql
-- Description: Realistic demo data for Peshawar, Pakistan
-- ============================================================================
-- ⚠️  ALL DATA IN THIS FILE IS FOR DEMONSTRATION PURPOSES ONLY
--     Names, phones, and addresses are fictional.
--     Do NOT use in production.
-- ============================================================================

-- ===========================================
-- DEMO USER IDs (pre-generated UUIDs)
-- ===========================================
-- We define fixed UUIDs so foreign keys can reference them consistently.
-- In production, these would come from auth.users via Supabase Auth.

-- Admin users
-- admin_1:  a0000001-0000-0000-0000-000000000001
-- admin_2:  a0000001-0000-0000-0000-000000000002
-- admin_3:  a0000001-0000-0000-0000-000000000003

-- Donor users (15)
-- donor_01: d0000001-0000-0000-0000-000000000001
-- donor_02: d0000001-0000-0000-0000-000000000002
-- donor_03: d0000001-0000-0000-0000-000000000003
-- donor_04: d0000001-0000-0000-0000-000000000004
-- donor_05: d0000001-0000-0000-0000-000000000005
-- donor_06: d0000001-0000-0000-0000-000000000006
-- donor_07: d0000001-0000-0000-0000-000000000007
-- donor_08: d0000001-0000-0000-0000-000000000008
-- donor_09: d0000001-0000-0000-0000-000000000009
-- donor_10: d0000001-0000-0000-0000-000000000010
-- donor_11: d0000001-0000-0000-0000-000000000011
-- donor_12: d0000001-0000-0000-0000-000000000012
-- donor_13: d0000001-0000-0000-0000-000000000013
-- donor_14: d0000001-0000-0000-0000-000000000014
-- donor_15: d0000001-0000-0000-0000-000000000015

-- Blood bank users (3)
-- bb_1:     b0000001-0000-0000-0000-000000000001
-- bb_2:     b0000001-0000-0000-0000-000000000002
-- bb_3:     b0000001-0000-0000-0000-000000000003

-- Patient/requester users (5)
-- patient_1: e0000001-0000-0000-0000-000000000001
-- patient_2: e0000001-0000-0000-0000-000000000002
-- patient_3: e0000001-0000-0000-0000-000000000003
-- patient_4: e0000001-0000-0000-0000-000000000004
-- patient_5: e0000001-0000-0000-0000-000000000005


-- ===========================================
-- STEP 1: Insert auth.users & auth.identities entries (for seed/demo)
-- NOTE: In production Supabase, users are created via Auth API.
--       This seed uses raw inserts with complete GoTrue-compliant fields
--       (identities, app_metadata with roles, and tokens) for demo purposes.
--       Password hash is for 'DemoPassword123!' using bcrypt.
-- ===========================================

-- We use a DO block so we can skip if auth schema isn't available in local dev
DO $$
DECLARE
  demo_password TEXT;
BEGIN
  BEGIN
    demo_password := extensions.crypt('DemoPassword123!', extensions.gen_salt('bf', 10));
  EXCEPTION WHEN OTHERS THEN
    demo_password := public.crypt('DemoPassword123!', public.gen_salt('bf', 10));
  END;
  -- Admin users
  INSERT INTO auth.users (
    id, instance_id, email, encrypted_password, email_confirmed_at,
    raw_app_meta_data, raw_user_meta_data, created_at, updated_at, aud, role,
    is_super_admin, confirmation_token, recovery_token, email_change_token_new,
    email_change, phone_change, phone_change_token, email_change_token_current, reauthentication_token
  )
  VALUES
    ('a0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', 'admin1@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"admin"}'::jsonb, '{"full_name":"Dr. Ahmad Khan","role":"admin"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('a0000001-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000000', 'admin2@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"admin"}'::jsonb, '{"full_name":"Dr. Fatima Bibi","role":"admin"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('a0000001-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000000', 'admin3@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"admin"}'::jsonb, '{"full_name":"Dr. Usman Ali","role":"admin"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', '')
  ON CONFLICT (id) DO UPDATE SET
    raw_app_meta_data = EXCLUDED.raw_app_meta_data,
    email_confirmed_at = EXCLUDED.email_confirmed_at,
    confirmation_token = EXCLUDED.confirmation_token,
    recovery_token = EXCLUDED.recovery_token,
    email_change_token_new = EXCLUDED.email_change_token_new,
    email_change = EXCLUDED.email_change,
    phone_change = EXCLUDED.phone_change,
    phone_change_token = EXCLUDED.phone_change_token,
    email_change_token_current = EXCLUDED.email_change_token_current,
    reauthentication_token = EXCLUDED.reauthentication_token;

  -- Donor users
  INSERT INTO auth.users (
    id, instance_id, email, encrypted_password, email_confirmed_at,
    raw_app_meta_data, raw_user_meta_data, created_at, updated_at, aud, role,
    is_super_admin, confirmation_token, recovery_token, email_change_token_new,
    email_change, phone_change, phone_change_token, email_change_token_current, reauthentication_token
  )
  VALUES
    ('d0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', 'donor01@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Muhammad Bilal","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000000', 'donor02@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Ayesha Noor","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000000', 'donor03@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Saeed Ullah","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000000', 'donor04@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Hina Gul","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000000', 'donor05@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Imran Shah","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000000', 'donor06@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Zainab Afridi","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000000', 'donor07@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Faisal Mehmood","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000000', 'donor08@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Sana Begum","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000000', 'donor09@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Tariq Jan","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000000', 'donor10@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Nadia Khattak","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000000', 'donor11@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Waqar Ahmed","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000000', 'donor12@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Rabia Yousafzai","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000013', '00000000-0000-0000-0000-000000000000', 'donor13@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Kamran Iqbal","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000014', '00000000-0000-0000-0000-000000000000', 'donor14@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Lubna Wazir","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('d0000001-0000-0000-0000-000000000015', '00000000-0000-0000-0000-000000000000', 'donor15@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"donor"}'::jsonb, '{"full_name":"Shahid Yousaf","role":"donor"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', '')
  ON CONFLICT (id) DO UPDATE SET
    raw_app_meta_data = EXCLUDED.raw_app_meta_data,
    email_confirmed_at = EXCLUDED.email_confirmed_at,
    confirmation_token = EXCLUDED.confirmation_token,
    recovery_token = EXCLUDED.recovery_token,
    email_change_token_new = EXCLUDED.email_change_token_new,
    email_change = EXCLUDED.email_change,
    phone_change = EXCLUDED.phone_change,
    phone_change_token = EXCLUDED.phone_change_token,
    email_change_token_current = EXCLUDED.email_change_token_current,
    reauthentication_token = EXCLUDED.reauthentication_token;

  -- Blood bank users
  INSERT INTO auth.users (
    id, instance_id, email, encrypted_password, email_confirmed_at,
    raw_app_meta_data, raw_user_meta_data, created_at, updated_at, aud, role,
    is_super_admin, confirmation_token, recovery_token, email_change_token_new,
    email_change, phone_change, phone_change_token, email_change_token_current, reauthentication_token
  )
  VALUES
    ('b0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', 'lrh.bloodbank@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"blood_bank"}'::jsonb, '{"full_name":"Lady Reading Hospital Blood Bank","role":"blood_bank"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('b0000001-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000000', 'hmc.bloodbank@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"blood_bank"}'::jsonb, '{"full_name":"Hayatabad Medical Complex Blood Bank","role":"blood_bank"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('b0000001-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000000', 'kth.bloodbank@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"blood_bank"}'::jsonb, '{"full_name":"Khyber Teaching Hospital Blood Bank","role":"blood_bank"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', '')
  ON CONFLICT (id) DO UPDATE SET
    raw_app_meta_data = EXCLUDED.raw_app_meta_data,
    email_confirmed_at = EXCLUDED.email_confirmed_at,
    confirmation_token = EXCLUDED.confirmation_token,
    recovery_token = EXCLUDED.recovery_token,
    email_change_token_new = EXCLUDED.email_change_token_new,
    email_change = EXCLUDED.email_change,
    phone_change = EXCLUDED.phone_change,
    phone_change_token = EXCLUDED.phone_change_token,
    email_change_token_current = EXCLUDED.email_change_token_current,
    reauthentication_token = EXCLUDED.reauthentication_token;

  -- Patient / requester users
  INSERT INTO auth.users (
    id, instance_id, email, encrypted_password, email_confirmed_at,
    raw_app_meta_data, raw_user_meta_data, created_at, updated_at, aud, role,
    is_super_admin, confirmation_token, recovery_token, email_change_token_new,
    email_change, phone_change, phone_change_token, email_change_token_current, reauthentication_token
  )
  VALUES
    ('e0000001-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000000', 'patient1@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"patient"}'::jsonb, '{"full_name":"Nasir Khan","role":"patient"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('e0000001-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000000', 'patient2@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"patient"}'::jsonb, '{"full_name":"Saima Gul","role":"patient"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('e0000001-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000000', 'patient3@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"patient"}'::jsonb, '{"full_name":"Zahid Ullah","role":"patient"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('e0000001-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000000', 'patient4@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"patient"}'::jsonb, '{"full_name":"Maryam Bibi","role":"patient"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', ''),
    ('e0000001-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000000', 'patient5@bloodbridge.demo', demo_password, now(), '{"provider":"email","providers":["email"],"role":"patient"}'::jsonb, '{"full_name":"Arif Hussain","role":"patient"}'::jsonb, now(), now(), 'authenticated', 'authenticated', false, '', '', '', '', '', '', '', '')
  ON CONFLICT (id) DO UPDATE SET
    raw_app_meta_data = EXCLUDED.raw_app_meta_data,
    email_confirmed_at = EXCLUDED.email_confirmed_at,
    confirmation_token = EXCLUDED.confirmation_token,
    recovery_token = EXCLUDED.recovery_token,
    email_change_token_new = EXCLUDED.email_change_token_new,
    email_change = EXCLUDED.email_change,
    phone_change = EXCLUDED.phone_change,
    phone_change_token = EXCLUDED.phone_change_token,
    email_change_token_current = EXCLUDED.email_change_token_current,
    reauthentication_token = EXCLUDED.reauthentication_token;

  -- Link auth.identities for all demo users
  INSERT INTO auth.identities (
    id, user_id, identity_data, provider, provider_id, last_sign_in_at, created_at, updated_at
  )
  SELECT
    u.id,
    u.id,
    jsonb_build_object('sub', u.id::text, 'email', lower(u.email)),
    'email',
    u.id::text,
    now(),
    now(),
    now()
  FROM auth.users u
  WHERE u.email LIKE '%@bloodbridge.demo'
    AND NOT EXISTS (
      SELECT 1 FROM auth.identities i WHERE i.user_id = u.id
    )
  ON CONFLICT DO NOTHING;

EXCEPTION
  WHEN others THEN
    RAISE NOTICE 'Could not insert auth.users or auth.identities: %', SQLERRM;
END;
$$;


-- ===========================================
-- STEP 2: PROFILES (DEMO)
-- ===========================================
INSERT INTO profiles (id, email, full_name, phone, role, city, district, area, address, latitude, longitude, is_verified, is_active) VALUES
-- Admins
('a0000001-0000-0000-0000-000000000001', 'admin1@bloodbridge.demo', 'Dr. Ahmad Khan', '+92-300-1234501', 'admin', 'Peshawar', 'Peshawar', 'Hayatabad', 'Phase 5, Hayatabad, Peshawar', 34.0017, 71.4448, true, true),
('a0000001-0000-0000-0000-000000000002', 'admin2@bloodbridge.demo', 'Dr. Fatima Bibi', '+92-300-1234502', 'admin', 'Peshawar', 'Peshawar', 'University Town', 'University Town, Peshawar', 34.0085, 71.4785, true, true),
('a0000001-0000-0000-0000-000000000003', 'admin3@bloodbridge.demo', 'Dr. Usman Ali', '+92-300-1234503', 'admin', 'Peshawar', 'Peshawar', 'Saddar', 'Saddar Road, Peshawar', 34.0253, 71.5784, true, true),

-- Donors
('d0000001-0000-0000-0000-000000000001', 'donor01@bloodbridge.demo', 'Muhammad Bilal', '+92-300-1234511', 'donor', 'Peshawar', 'Peshawar', 'Hayatabad', 'Phase 3, Street 5, Hayatabad', 34.0020, 71.4460, true, true),
('d0000001-0000-0000-0000-000000000002', 'donor02@bloodbridge.demo', 'Ayesha Noor', '+92-300-1234512', 'donor', 'Peshawar', 'Peshawar', 'University Town', 'Sector D, University Town', 34.0090, 71.4790, true, true),
('d0000001-0000-0000-0000-000000000003', 'donor03@bloodbridge.demo', 'Saeed Ullah', '+92-300-1234513', 'donor', 'Peshawar', 'Peshawar', 'Saddar', 'Saddar Bazaar, Peshawar', 34.0255, 71.5780, true, true),
('d0000001-0000-0000-0000-000000000004', 'donor04@bloodbridge.demo', 'Hina Gul', '+92-300-1234514', 'donor', 'Peshawar', 'Peshawar', 'Gulbahar', 'Gulbahar Colony No. 2', 34.0312, 71.5656, true, true),
('d0000001-0000-0000-0000-000000000005', 'donor05@bloodbridge.demo', 'Imran Shah', '+92-300-1234515', 'donor', 'Peshawar', 'Peshawar', 'Hayatabad', 'Phase 7, Hayatabad', 34.0005, 71.4420, true, true),
('d0000001-0000-0000-0000-000000000006', 'donor06@bloodbridge.demo', 'Zainab Afridi', '+92-300-1234516', 'donor', 'Peshawar', 'Peshawar', 'University Town', 'Sector B, University Town', 34.0080, 71.4800, true, true),
('d0000001-0000-0000-0000-000000000007', 'donor07@bloodbridge.demo', 'Faisal Mehmood', '+92-300-1234517', 'donor', 'Peshawar', 'Peshawar', 'Saddar', 'Cinema Road, Saddar', 34.0260, 71.5790, true, true),
('d0000001-0000-0000-0000-000000000008', 'donor08@bloodbridge.demo', 'Sana Begum', '+92-300-1234518', 'donor', 'Peshawar', 'Peshawar', 'Gulbahar', 'Gulbahar Main Road', 34.0315, 71.5660, true, true),
('d0000001-0000-0000-0000-000000000009', 'donor09@bloodbridge.demo', 'Tariq Jan', '+92-300-1234519', 'donor', 'Peshawar', 'Peshawar', 'Board Bazaar', 'Board Bazaar, Peshawar', 34.0180, 71.5400, true, true),
('d0000001-0000-0000-0000-000000000010', 'donor10@bloodbridge.demo', 'Nadia Khattak', '+92-300-1234520', 'donor', 'Peshawar', 'Peshawar', 'Hayatabad', 'Phase 1, Hayatabad', 34.0030, 71.4500, true, true),
('d0000001-0000-0000-0000-000000000011', 'donor11@bloodbridge.demo', 'Waqar Ahmed', '+92-300-1234521', 'donor', 'Peshawar', 'Peshawar', 'Cantonment', 'Peshawar Cantonment Area', 34.0150, 71.5600, true, true),
('d0000001-0000-0000-0000-000000000012', 'donor12@bloodbridge.demo', 'Rabia Yousafzai', '+92-300-1234522', 'donor', 'Peshawar', 'Peshawar', 'University Town', 'Sector C, University Town', 34.0088, 71.4795, true, true),
('d0000001-0000-0000-0000-000000000013', 'donor13@bloodbridge.demo', 'Kamran Iqbal', '+92-300-1234523', 'donor', 'Peshawar', 'Peshawar', 'Dalazak Road', 'Dalazak Road, Peshawar', 34.0350, 71.5500, true, true),
('d0000001-0000-0000-0000-000000000014', 'donor14@bloodbridge.demo', 'Lubna Wazir', '+92-300-1234524', 'donor', 'Peshawar', 'Peshawar', 'Gulbahar', 'Gulbahar No. 1, Peshawar', 34.0310, 71.5650, true, true),
('d0000001-0000-0000-0000-000000000015', 'donor15@bloodbridge.demo', 'Shahid Yousaf', '+92-300-1234525', 'donor', 'Peshawar', 'Peshawar', 'Saddar', 'Khyber Bazaar, Peshawar', 34.0240, 71.5770, false, true),

-- Blood bank profiles
('b0000001-0000-0000-0000-000000000001', 'lrh.bloodbank@bloodbridge.demo', 'Lady Reading Hospital Blood Bank', '+92-91-9211430', 'blood_bank', 'Peshawar', 'Peshawar', 'Saddar', 'Lady Reading Hospital, Soekarno Road', 34.0253, 71.5784, true, true),
('b0000001-0000-0000-0000-000000000002', 'hmc.bloodbank@bloodbridge.demo', 'Hayatabad Medical Complex Blood Bank', '+92-91-9217140', 'blood_bank', 'Peshawar', 'Peshawar', 'Hayatabad', 'Phase 4, Hayatabad', 34.0017, 71.4448, true, true),
('b0000001-0000-0000-0000-000000000003', 'kth.bloodbank@bloodbridge.demo', 'Khyber Teaching Hospital Blood Bank', '+92-91-9216340', 'blood_bank', 'Peshawar', 'Peshawar', 'University Town', 'University Road, Peshawar', 34.0085, 71.4785, true, true),

-- Patient / requester profiles
('e0000001-0000-0000-0000-000000000001', 'patient1@bloodbridge.demo', 'Nasir Khan', '+92-300-1234531', 'patient', 'Peshawar', 'Peshawar', 'Hayatabad', 'Phase 6, Hayatabad', 34.0010, 71.4440, false, true),
('e0000001-0000-0000-0000-000000000002', 'patient2@bloodbridge.demo', 'Saima Gul', '+92-300-1234532', 'patient', 'Peshawar', 'Peshawar', 'Gulbahar', 'Gulbahar Colony, Peshawar', 34.0314, 71.5658, false, true),
('e0000001-0000-0000-0000-000000000003', 'patient3@bloodbridge.demo', 'Zahid Ullah', '+92-300-1234533', 'patient', 'Peshawar', 'Peshawar', 'Saddar', 'Saddar Road, Peshawar', 34.0250, 71.5780, false, true),
('e0000001-0000-0000-0000-000000000004', 'patient4@bloodbridge.demo', 'Maryam Bibi', '+92-300-1234534', 'patient', 'Peshawar', 'Peshawar', 'University Town', 'University Town, Peshawar', 34.0082, 71.4788, false, true),
('e0000001-0000-0000-0000-000000000005', 'patient5@bloodbridge.demo', 'Arif Hussain', '+92-300-1234535', 'patient', 'Peshawar', 'Peshawar', 'Cantonment', 'Peshawar Cantt', 34.0155, 71.5610, false, true)
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 3: DONORS TABLE (DEMO)
-- ===========================================
-- Fixed donor record IDs for referencing
-- dr_01: dd000001-0000-0000-0000-000000000001 ... dr_15: dd000001-0000-0000-0000-000000000015

INSERT INTO donors (id, user_id, blood_group, date_of_birth, gender, weight, last_donation_date, total_donations, is_available, availability_radius_km, consent_notifications, medical_conditions, is_eligible, verified_at, verified_by) VALUES
('dd000001-0000-0000-0000-000000000001', 'd0000001-0000-0000-0000-000000000001', 'A+',  '1995-03-15', 'male',   75, '2026-08-10', 5,  true,  10, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('dd000001-0000-0000-0000-000000000002', 'd0000001-0000-0000-0000-000000000002', 'B+',  '1998-07-22', 'female', 58, '2026-09-01', 3,  true,  15, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('dd000001-0000-0000-0000-000000000003', 'd0000001-0000-0000-0000-000000000003', 'O+',  '1990-11-05', 'male',   82, '2026-07-20', 8,  true,  20, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('dd000001-0000-0000-0000-000000000004', 'd0000001-0000-0000-0000-000000000004', 'AB+', '1993-01-30', 'female', 62, NULL,          0,  true,  10, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000002'),
('dd000001-0000-0000-0000-000000000005', 'd0000001-0000-0000-0000-000000000005', 'A-',  '1988-06-12', 'male',   70, '2026-06-15', 12, true,  15, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000002'),
('dd000001-0000-0000-0000-000000000006', 'd0000001-0000-0000-0000-000000000006', 'O-',  '1996-09-18', 'female', 55, '2026-08-25', 4,  true,  10, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000002'),
('dd000001-0000-0000-0000-000000000007', 'd0000001-0000-0000-0000-000000000007', 'B-',  '1992-04-08', 'male',   78, '2026-05-10', 6,  true,  20, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000003'),
('dd000001-0000-0000-0000-000000000008', 'd0000001-0000-0000-0000-000000000008', 'A+',  '1999-12-25', 'female', 60, NULL,          0,  true,  10, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000003'),
('dd000001-0000-0000-0000-000000000009', 'd0000001-0000-0000-0000-000000000009', 'O+',  '1987-08-14', 'male',   85, '2026-09-15', 15, true,  25, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('dd000001-0000-0000-0000-000000000010', 'd0000001-0000-0000-0000-000000000010', 'AB-', '1994-02-28', 'female', 57, '2026-07-01', 2,  true,  10, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('dd000001-0000-0000-0000-000000000011', 'd0000001-0000-0000-0000-000000000011', 'B+',  '1991-05-20', 'male',   73, '2026-04-18', 7,  true,  15, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000002'),
('dd000001-0000-0000-0000-000000000012', 'd0000001-0000-0000-0000-000000000012', 'A-',  '1997-10-10', 'female', 64, NULL,          0,  true,  10, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000003'),
('dd000001-0000-0000-0000-000000000013', 'd0000001-0000-0000-0000-000000000013', 'O-',  '1985-07-07', 'male',   80, '2026-08-01', 20, true,  30, true, NULL, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('dd000001-0000-0000-0000-000000000014', 'd0000001-0000-0000-0000-000000000014', 'AB+', '2000-03-03', 'female', 52, NULL,          0,  false, 10, true, 'Mild anemia - under treatment (DEMO)', false, NULL, NULL),
('dd000001-0000-0000-0000-000000000015', 'd0000001-0000-0000-0000-000000000015', 'B-',  '1989-11-11', 'male',   76, '2026-03-20', 9,  false, 15, false, NULL, true, now(), 'a0000001-0000-0000-0000-000000000003')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 4: BLOOD BANKS (DEMO)
-- ===========================================
-- Fixed blood bank IDs
-- bb_rec_1: bb000001-0000-0000-0000-000000000001 (Lady Reading Hospital)
-- bb_rec_2: bb000001-0000-0000-0000-000000000002 (Hayatabad Medical Complex)
-- bb_rec_3: bb000001-0000-0000-0000-000000000003 (Khyber Teaching Hospital)

INSERT INTO blood_banks (id, user_id, name, license_number, type, phone, email, address, city, area, latitude, longitude, operating_hours, is_verified, is_active, verified_at, verified_by) VALUES
('bb000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001', 'Lady Reading Hospital Blood Bank', 'LIC-KPK-BB-001', 'both', '+92-91-9211430', 'bloodbank@lrh.demo', 'Lady Reading Hospital, Soekarno Road, Peshawar', 'Peshawar', 'Saddar', 34.0253, 71.5784, '24/7', true, true, now(), 'a0000001-0000-0000-0000-000000000001'),
('bb000001-0000-0000-0000-000000000002', 'b0000001-0000-0000-0000-000000000002', 'Hayatabad Medical Complex Blood Bank', 'LIC-KPK-BB-002', 'both', '+92-91-9217140', 'bloodbank@hmc.demo', 'Hayatabad Medical Complex, Phase 4, Hayatabad, Peshawar', 'Peshawar', 'Hayatabad', 34.0017, 71.4448, '24/7', true, true, now(), 'a0000001-0000-0000-0000-000000000002'),
('bb000001-0000-0000-0000-000000000003', 'b0000001-0000-0000-0000-000000000003', 'Khyber Teaching Hospital Blood Bank', 'LIC-KPK-BB-003', 'hospital', '+92-91-9216340', 'bloodbank@kth.demo', 'Khyber Teaching Hospital, University Road, Peshawar', 'Peshawar', 'University Town', 34.0085, 71.4785, '08:00 - 22:00', true, true, now(), 'a0000001-0000-0000-0000-000000000003')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 5: BLOOD REQUESTS (DEMO)
-- ===========================================
-- request_number is auto-generated by trigger, so we set DEFAULT for it.
-- Fixed request IDs:
-- req_1: cc000001-0000-0000-0000-000000000001
-- req_2: cc000001-0000-0000-0000-000000000002
-- req_3: cc000001-0000-0000-0000-000000000003
-- req_4: cc000001-0000-0000-0000-000000000004
-- req_5: cc000001-0000-0000-0000-000000000005

INSERT INTO blood_requests (id, requester_id, patient_name, blood_group, units_needed, hospital_name, hospital_address, city, area, latitude, longitude, emergency_level, required_by, contact_name, contact_phone, additional_notes, status, units_fulfilled, fulfilled_at) VALUES
('cc000001-0000-0000-0000-000000000001', 'e0000001-0000-0000-0000-000000000001', 'Ali Ahmad (DEMO)', 'A+', 3, 'Lady Reading Hospital', 'Soekarno Road, Peshawar', 'Peshawar', 'Saddar', 34.0253, 71.5784, 'critical', now() + interval '6 hours', 'Nasir Khan', '+92-300-1234531', 'Patient in ICU, urgent surgery scheduled (DEMO DATA)', 'pending', 0, NULL),
('cc000001-0000-0000-0000-000000000002', 'e0000001-0000-0000-0000-000000000002', 'Sajida Bibi (DEMO)', 'O+', 2, 'Hayatabad Medical Complex', 'Phase 4, Hayatabad', 'Peshawar', 'Hayatabad', 34.0017, 71.4448, 'urgent', now() + interval '24 hours', 'Saima Gul', '+92-300-1234532', 'Post-surgery blood replacement needed (DEMO DATA)', 'matching', 0, NULL),
('cc000001-0000-0000-0000-000000000003', 'e0000001-0000-0000-0000-000000000003', 'Farhan Ullah (DEMO)', 'B+', 1, 'Khyber Teaching Hospital', 'University Road, Peshawar', 'Peshawar', 'University Town', 34.0085, 71.4785, 'normal', now() + interval '72 hours', 'Zahid Ullah', '+92-300-1234533', 'Thalassemia patient, regular transfusion (DEMO DATA)', 'matched', 0, NULL),
('cc000001-0000-0000-0000-000000000004', 'e0000001-0000-0000-0000-000000000004', 'Kiran Naz (DEMO)', 'AB-', 2, 'Lady Reading Hospital', 'Soekarno Road, Peshawar', 'Peshawar', 'Saddar', 34.0253, 71.5784, 'urgent', now() + interval '12 hours', 'Maryam Bibi', '+92-300-1234534', 'Rare blood type, difficult to find donors (DEMO DATA)', 'donor_confirmed', 1, NULL),
('cc000001-0000-0000-0000-000000000005', 'e0000001-0000-0000-0000-000000000005', 'Usman Ghani (DEMO)', 'O-', 4, 'Hayatabad Medical Complex', 'Phase 4, Hayatabad', 'Peshawar', 'Hayatabad', 34.0017, 71.4448, 'critical', now() - interval '48 hours', 'Arif Hussain', '+92-300-1234535', 'Emergency trauma case - fulfilled successfully (DEMO DATA)', 'fulfilled', 4, now() - interval '46 hours')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 6: INVENTORY BATCHES (DEMO)
-- ===========================================
INSERT INTO inventory_batches (id, blood_bank_id, blood_group, units_available, collection_date, expiry_date, screening_status, availability_status, batch_number, notes) VALUES
-- Lady Reading Hospital inventory
('1b000001-0000-0000-0000-000000000001', 'bb000001-0000-0000-0000-000000000001', 'A+',  12, '2026-10-20', '2027-02-17', 'passed', 'available', 'LRH-2026-001', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000002', 'bb000001-0000-0000-0000-000000000001', 'B+',  8,  '2026-10-22', '2027-02-19', 'passed', 'available', 'LRH-2026-002', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000003', 'bb000001-0000-0000-0000-000000000001', 'O+',  15, '2026-10-25', '2027-02-22', 'passed', 'available', 'LRH-2026-003', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000004', 'bb000001-0000-0000-0000-000000000001', 'AB+', 3,  '2026-10-18', '2027-02-15', 'passed', 'available', 'LRH-2026-004', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000005', 'bb000001-0000-0000-0000-000000000001', 'O-',  5,  '2026-10-15', '2027-02-12', 'passed', 'available', 'LRH-2026-005', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000006', 'bb000001-0000-0000-0000-000000000001', 'A-',  2,  '2026-09-10', '2027-01-08', 'passed', 'available', 'LRH-2026-006', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000007', 'bb000001-0000-0000-0000-000000000001', 'B-',  1,  '2026-08-01', '2026-11-29', 'passed', 'available', 'LRH-2026-007', 'DEMO batch - nearing expiry'),
('1b000001-0000-0000-0000-000000000008', 'bb000001-0000-0000-0000-000000000001', 'AB-', 1,  '2026-10-28', '2027-02-25', 'pending', 'quarantined', 'LRH-2026-008', 'DEMO batch - awaiting screening'),

-- Hayatabad Medical Complex inventory
('1b000001-0000-0000-0000-000000000009', 'bb000001-0000-0000-0000-000000000002', 'A+',  10, '2026-10-21', '2027-02-18', 'passed', 'available', 'HMC-2026-001', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000010', 'bb000001-0000-0000-0000-000000000002', 'B+',  6,  '2026-10-23', '2027-02-20', 'passed', 'available', 'HMC-2026-002', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000011', 'bb000001-0000-0000-0000-000000000002', 'O+',  20, '2026-10-26', '2027-02-23', 'passed', 'available', 'HMC-2026-003', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000012', 'bb000001-0000-0000-0000-000000000002', 'O-',  4,  '2026-10-19', '2027-02-16', 'passed', 'available', 'HMC-2026-004', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000013', 'bb000001-0000-0000-0000-000000000002', 'AB+', 2,  '2026-10-10', '2027-02-07', 'passed', 'reserved', 'HMC-2026-005', 'DEMO batch - reserved for surgery'),
('1b000001-0000-0000-0000-000000000014', 'bb000001-0000-0000-0000-000000000002', 'A-',  3,  '2026-10-24', '2027-02-21', 'passed', 'available', 'HMC-2026-006', 'DEMO batch'),

-- Khyber Teaching Hospital inventory
('1b000001-0000-0000-0000-000000000015', 'bb000001-0000-0000-0000-000000000003', 'A+',  7,  '2026-10-22', '2027-02-19', 'passed', 'available', 'KTH-2026-001', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000016', 'bb000001-0000-0000-0000-000000000003', 'B+',  5,  '2026-10-20', '2027-02-17', 'passed', 'available', 'KTH-2026-002', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000017', 'bb000001-0000-0000-0000-000000000003', 'O+',  11, '2026-10-27', '2027-02-24', 'passed', 'available', 'KTH-2026-003', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000018', 'bb000001-0000-0000-0000-000000000003', 'O-',  3,  '2026-10-16', '2027-02-13', 'passed', 'available', 'KTH-2026-004', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000019', 'bb000001-0000-0000-0000-000000000003', 'B-',  2,  '2026-10-25', '2027-02-22', 'passed', 'available', 'KTH-2026-005', 'DEMO batch'),
('1b000001-0000-0000-0000-000000000020', 'bb000001-0000-0000-0000-000000000003', 'AB-', 1,  '2026-10-12', '2027-02-09', 'passed', 'available', 'KTH-2026-006', 'DEMO batch - rare type')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 7: DONOR INVITATIONS (DEMO)
-- ===========================================
INSERT INTO donor_invitations (id, request_id, donor_id, status, match_score, match_reasons, distance_km, invited_at, responded_at, response_notes) VALUES
-- Invitations for Request 1 (A+ critical at LRH)
('d1000001-0000-0000-0000-000000000001', 'cc000001-0000-0000-0000-000000000001', 'dd000001-0000-0000-0000-000000000001', 'pending', 95.0, '{"blood_match": "exact", "distance": "close", "experience": "experienced"}'::jsonb, 3.2, now() - interval '1 hour', NULL, NULL),
('d1000001-0000-0000-0000-000000000002', 'cc000001-0000-0000-0000-000000000001', 'dd000001-0000-0000-0000-000000000008', 'pending', 90.0, '{"blood_match": "exact", "distance": "moderate", "experience": "new"}'::jsonb, 5.8, now() - interval '1 hour', NULL, NULL),

-- Invitations for Request 2 (O+ urgent at HMC)
('d1000001-0000-0000-0000-000000000003', 'cc000001-0000-0000-0000-000000000002', 'dd000001-0000-0000-0000-000000000003', 'accepted', 92.0, '{"blood_match": "exact", "distance": "close", "experience": "veteran"}'::jsonb, 2.1, now() - interval '4 hours', now() - interval '3 hours', 'Happy to help! (DEMO)'),
('d1000001-0000-0000-0000-000000000004', 'cc000001-0000-0000-0000-000000000002', 'dd000001-0000-0000-0000-000000000009', 'declined', 88.0, '{"blood_match": "exact", "distance": "moderate"}'::jsonb, 8.5, now() - interval '4 hours', now() - interval '2 hours', 'Sorry, traveling out of city (DEMO)'),

-- Invitations for Request 3 (B+ normal at KTH)
('d1000001-0000-0000-0000-000000000005', 'cc000001-0000-0000-0000-000000000003', 'dd000001-0000-0000-0000-000000000002', 'accepted', 85.0, '{"blood_match": "exact", "distance": "close"}'::jsonb, 1.5, now() - interval '12 hours', now() - interval '10 hours', 'Available anytime (DEMO)'),

-- Invitations for Request 4 (AB- urgent at LRH)
('d1000001-0000-0000-0000-000000000006', 'cc000001-0000-0000-0000-000000000004', 'dd000001-0000-0000-0000-000000000010', 'accepted', 97.0, '{"blood_match": "exact", "distance": "close", "rare_type": true}'::jsonb, 4.0, now() - interval '6 hours', now() - interval '5 hours', 'On my way to the hospital (DEMO)'),

-- Invitations for Request 5 (O- critical at HMC - fulfilled)
('d1000001-0000-0000-0000-000000000007', 'cc000001-0000-0000-0000-000000000005', 'dd000001-0000-0000-0000-000000000006', 'accepted', 96.0, '{"blood_match": "exact", "universal_donor": true}'::jsonb, 3.5, now() - interval '50 hours', now() - interval '49 hours', 'Donated successfully (DEMO)'),
('d1000001-0000-0000-0000-000000000008', 'cc000001-0000-0000-0000-000000000005', 'dd000001-0000-0000-0000-000000000013', 'accepted', 94.0, '{"blood_match": "exact", "universal_donor": true, "veteran": true}'::jsonb, 6.2, now() - interval '50 hours', now() - interval '48 hours', 'Donated successfully (DEMO)')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 8: DONATION RECORDS (DEMO)
-- ===========================================
INSERT INTO donation_records (id, donor_id, request_id, blood_bank_id, blood_group, units_donated, donation_date, status, notes, verified_by) VALUES
-- Past donations from fulfilled request
('d2000001-0000-0000-0000-000000000001', 'dd000001-0000-0000-0000-000000000006', 'cc000001-0000-0000-0000-000000000005', 'bb000001-0000-0000-0000-000000000002', 'O-', 2, CURRENT_DATE - 2, 'completed', 'Emergency trauma donation (DEMO)', 'a0000001-0000-0000-0000-000000000001'),
('d2000001-0000-0000-0000-000000000002', 'dd000001-0000-0000-0000-000000000013', 'cc000001-0000-0000-0000-000000000005', 'bb000001-0000-0000-0000-000000000002', 'O-', 2, CURRENT_DATE - 2, 'completed', 'Emergency trauma donation (DEMO)', 'a0000001-0000-0000-0000-000000000001'),
-- Scheduled donation for request 4
('d2000001-0000-0000-0000-000000000003', 'dd000001-0000-0000-0000-000000000010', 'cc000001-0000-0000-0000-000000000004', 'bb000001-0000-0000-0000-000000000001', 'AB-', 1, CURRENT_DATE, 'scheduled', 'Scheduled for today (DEMO)', NULL),
-- Historical donations (not tied to specific requests)
('d2000001-0000-0000-0000-000000000004', 'dd000001-0000-0000-0000-000000000001', NULL, 'bb000001-0000-0000-0000-000000000001', 'A+', 1, '2026-08-10', 'completed', 'Regular donation (DEMO)', 'a0000001-0000-0000-0000-000000000002'),
('d2000001-0000-0000-0000-000000000005', 'dd000001-0000-0000-0000-000000000009', NULL, 'bb000001-0000-0000-0000-000000000003', 'O+', 1, '2026-09-15', 'completed', 'Regular donation (DEMO)', 'a0000001-0000-0000-0000-000000000003')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 9: NOTIFICATIONS (DEMO)
-- ===========================================
INSERT INTO notifications (id, user_id, title, message, type, reference_type, reference_id, is_read, read_at) VALUES
-- Notifications for donor 1 (Muhammad Bilal)
('f0000001-0000-0000-0000-000000000001', 'd0000001-0000-0000-0000-000000000001', 'New Blood Request Match', 'A critical A+ blood request has been raised at Lady Reading Hospital. You are a potential match! (DEMO)', 'invitation', 'blood_request', 'cc000001-0000-0000-0000-000000000001', false, NULL),
-- Notifications for donor 3 (Saeed Ullah)
('f0000001-0000-0000-0000-000000000002', 'd0000001-0000-0000-0000-000000000003', 'Invitation Accepted', 'Thank you for accepting the blood donation invitation for O+ blood at HMC. Please arrive by tomorrow. (DEMO)', 'invitation', 'donor_invitation', 'd1000001-0000-0000-0000-000000000003', true, now() - interval '2 hours'),
-- Notifications for patient 1 (Nasir Khan)
('f0000001-0000-0000-0000-000000000003', 'e0000001-0000-0000-0000-000000000001', 'Request Submitted', 'Your blood request BR has been submitted successfully. We are matching donors now. (DEMO)', 'request_update', 'blood_request', 'cc000001-0000-0000-0000-000000000001', true, now() - interval '30 minutes'),
-- Notifications for patient 5 (Arif Hussain)
('f0000001-0000-0000-0000-000000000004', 'e0000001-0000-0000-0000-000000000005', 'Request Fulfilled', 'Your blood request for O- blood has been fulfilled! 4 units have been arranged. (DEMO)', 'request_update', 'blood_request', 'cc000001-0000-0000-0000-000000000005', true, now() - interval '46 hours'),
-- System notification for admin
('f0000001-0000-0000-0000-000000000005', 'a0000001-0000-0000-0000-000000000001', 'System Alert', 'Blood inventory for B- at LRH is running low (1 unit remaining, nearing expiry). (DEMO)', 'system', 'inventory_batch', '1b000001-0000-0000-0000-000000000007', false, NULL),
-- Verification notification
('f0000001-0000-0000-0000-000000000006', 'd0000001-0000-0000-0000-000000000001', 'Profile Verified', 'Your donor profile has been verified by the admin team. You can now receive donation requests. (DEMO)', 'verification', 'profile', 'd0000001-0000-0000-0000-000000000001', true, now() - interval '7 days'),
-- Reminder for donor 6
('f0000001-0000-0000-0000-000000000007', 'd0000001-0000-0000-0000-000000000006', 'Donation Reminder', 'It has been 56+ days since your last donation. You are now eligible to donate again! (DEMO)', 'reminder', NULL, NULL, false, NULL)
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 10: REQUEST STATUS HISTORY (DEMO)
-- ===========================================
INSERT INTO request_status_history (id, request_id, old_status, new_status, changed_by, notes) VALUES
-- History for fulfilled request 5
('f5000001-0000-0000-0000-000000000001', 'cc000001-0000-0000-0000-000000000005', NULL, 'pending', 'e0000001-0000-0000-0000-000000000005', 'Request created (DEMO)'),
('f5000001-0000-0000-0000-000000000002', 'cc000001-0000-0000-0000-000000000005', 'pending', 'matching', 'a0000001-0000-0000-0000-000000000001', 'AI matching started (DEMO)'),
('f5000001-0000-0000-0000-000000000003', 'cc000001-0000-0000-0000-000000000005', 'matching', 'matched', 'a0000001-0000-0000-0000-000000000001', '2 donors matched (DEMO)'),
('f5000001-0000-0000-0000-000000000004', 'cc000001-0000-0000-0000-000000000005', 'matched', 'donor_confirmed', 'a0000001-0000-0000-0000-000000000001', 'Both donors confirmed (DEMO)'),
('f5000001-0000-0000-0000-000000000005', 'cc000001-0000-0000-0000-000000000005', 'donor_confirmed', 'fulfilled', 'a0000001-0000-0000-0000-000000000001', '4 units donated successfully (DEMO)'),
-- History for current request 1
('f5000001-0000-0000-0000-000000000006', 'cc000001-0000-0000-0000-000000000001', NULL, 'pending', 'e0000001-0000-0000-0000-000000000001', 'Critical request created (DEMO)'),
-- History for request 2
('f5000001-0000-0000-0000-000000000007', 'cc000001-0000-0000-0000-000000000002', NULL, 'pending', 'e0000001-0000-0000-0000-000000000002', 'Request created (DEMO)'),
('f5000001-0000-0000-0000-000000000008', 'cc000001-0000-0000-0000-000000000002', 'pending', 'matching', 'a0000001-0000-0000-0000-000000000001', 'AI matching in progress (DEMO)')
ON CONFLICT (id) DO NOTHING;


-- ===========================================
-- STEP 11: AUDIT LOGS (DEMO)
-- ===========================================
INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, details, ip_address) VALUES
('a1000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', 'verify_donor', 'donor', 'dd000001-0000-0000-0000-000000000001', '{"donor_name": "Muhammad Bilal", "blood_group": "A+", "note": "DEMO audit log"}'::jsonb, '192.168.1.100'),
('a1000001-0000-0000-0000-000000000002', 'a0000001-0000-0000-0000-000000000001', 'verify_blood_bank', 'blood_bank', 'bb000001-0000-0000-0000-000000000001', '{"bank_name": "Lady Reading Hospital Blood Bank", "note": "DEMO audit log"}'::jsonb, '192.168.1.100'),
('a1000001-0000-0000-0000-000000000003', 'e0000001-0000-0000-0000-000000000001', 'create_request', 'blood_request', 'cc000001-0000-0000-0000-000000000001', '{"blood_group": "A+", "units": 3, "emergency": "critical", "note": "DEMO audit log"}'::jsonb, '192.168.1.105'),
('a1000001-0000-0000-0000-000000000004', 'd0000001-0000-0000-0000-000000000003', 'accept_invitation', 'donor_invitation', 'd1000001-0000-0000-0000-000000000003', '{"request_id": "cc000001-0000-0000-0000-000000000002", "note": "DEMO audit log"}'::jsonb, '192.168.1.110'),
('a1000001-0000-0000-0000-000000000005', 'a0000001-0000-0000-0000-000000000001', 'fulfill_request', 'blood_request', 'cc000001-0000-0000-0000-000000000005', '{"units_fulfilled": 4, "note": "DEMO audit log"}'::jsonb, '192.168.1.100')
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- ⚠️  END OF DEMO SEED DATA
--     All data above is fictional and for demonstration purposes only.
--     Do NOT use in production environments.
-- ============================================================================
