-- ============================================================================
-- BloodBridge: Supabase Auth Demo Account Repair Script
-- File: supabase/repair_auth.sql
-- Description:
--   Repairs all 26 demo accounts (@bloodbridge.demo) directly in Supabase Auth
--   without deleting any records or altering foreign keys.
--
-- Safety Guarantees:
--   - Does NOT delete or recreate any users. All UUIDs are strictly preserved.
--   - Preserves all 26 profiles, 15 donors, 3 blood banks, and relations.
--   - Computes bcrypt hash dynamically via pgcrypto crypt() for 'DemoPassword123!'.
--   - No unverified fallback hashes.
--   - Does NOT modify last_sign_in_at audit timestamps.
--   - Does NOT modify generated columns (confirmed_at is automatically computed from email_confirmed_at).
--   - Sets GoTrue string fields to '' to prevent Go runtime scan errors.
--   - Populates trusted raw_app_meta_data with matching roles.
--   - Safely creates auth.identities adapting to column data types (UUID vs TEXT).
--   - Synchronizes public.profiles roles with intended demo roles.
-- ============================================================================

DO $$
DECLARE
  demo_pw_hash TEXT;
  repaired_users INT := 0;
  repaired_identities INT := 0;
  repaired_profiles INT := 0;
  id_data_type TEXT;
BEGIN
  -- 1. Compute valid bcrypt hash for 'DemoPassword123!' using pgcrypto
  BEGIN
    demo_pw_hash := extensions.crypt('DemoPassword123!', extensions.gen_salt('bf', 10));
  EXCEPTION WHEN OTHERS THEN
    BEGIN
      demo_pw_hash := public.crypt('DemoPassword123!', public.gen_salt('bf', 10));
    EXCEPTION WHEN OTHERS THEN
      RAISE EXCEPTION 'pgcrypto crypt() function is not available. Please verify pgcrypto is enabled in extensions.';
    END;
  END;

  -- 2. Update auth.users for all 26 demo accounts
  --    Note: confirmed_at is a generated column (computed from email_confirmed_at)
  --    and is omitted to prevent PostgreSQL error 428C9.
  --    Note: last_sign_in_at is deliberately untouched to preserve sign-in history.
  UPDATE auth.users
  SET
    encrypted_password = demo_pw_hash,
    email_confirmed_at = COALESCE(email_confirmed_at, now()),
    raw_app_meta_data = jsonb_build_object(
      'provider', 'email',
      'providers', jsonb_build_array('email'),
      'role', COALESCE(raw_user_meta_data->>'role', 'patient')
    ),
    raw_user_meta_data = COALESCE(raw_user_meta_data, '{}'::jsonb),
    is_super_admin = COALESCE(is_super_admin, false),
    aud = 'authenticated',
    role = 'authenticated',
    confirmation_token = COALESCE(confirmation_token, ''),
    recovery_token = COALESCE(recovery_token, ''),
    email_change_token_new = COALESCE(email_change_token_new, ''),
    email_change = COALESCE(email_change, ''),
    phone_change = COALESCE(phone_change, ''),
    phone_change_token = COALESCE(phone_change_token, ''),
    email_change_token_current = COALESCE(email_change_token_current, ''),
    reauthentication_token = COALESCE(reauthentication_token, ''),
    updated_at = now()
  WHERE email LIKE '%@bloodbridge.demo';

  GET DIAGNOSTICS repaired_users = ROW_COUNT;
  RAISE NOTICE 'Updated % demo users in auth.users', repaired_users;

  -- 3. Populate missing auth.identities with column type safety
  --    Note: email is a generated column and is omitted from the column list.
  SELECT data_type
  INTO id_data_type
  FROM information_schema.columns
  WHERE table_schema = 'auth' AND table_name = 'identities' AND column_name = 'id';

  IF id_data_type = 'uuid' THEN
    INSERT INTO auth.identities (
      id, user_id, identity_data, provider, provider_id, created_at, updated_at
    )
    SELECT
      u.id,
      u.id,
      jsonb_build_object('sub', u.id::text, 'email', lower(u.email)),
      'email',
      u.id::text,
      now(),
      now()
    FROM auth.users u
    WHERE u.email LIKE '%@bloodbridge.demo'
      AND NOT EXISTS (
        SELECT 1 FROM auth.identities i WHERE i.user_id = u.id
      )
    ON CONFLICT DO NOTHING;
  ELSE
    INSERT INTO auth.identities (
      id, user_id, identity_data, provider, provider_id, created_at, updated_at
    )
    SELECT
      u.id::text,
      u.id,
      jsonb_build_object('sub', u.id::text, 'email', lower(u.email)),
      'email',
      u.id::text,
      now(),
      now()
    FROM auth.users u
    WHERE u.email LIKE '%@bloodbridge.demo'
      AND NOT EXISTS (
        SELECT 1 FROM auth.identities i WHERE i.user_id = u.id
      )
    ON CONFLICT DO NOTHING;
  END IF;

  GET DIAGNOSTICS repaired_identities = ROW_COUNT;
  RAISE NOTICE 'Inserted % missing identities in auth.identities', repaired_identities;

  -- 4. Sync public.profiles role with raw_app_meta_data to ensure consistency
  UPDATE public.profiles p
  SET role = u.raw_app_meta_data->>'role'
  FROM auth.users u
  WHERE p.id = u.id
    AND u.raw_app_meta_data->>'role' IS NOT NULL
    AND p.role <> u.raw_app_meta_data->>'role';

  GET DIAGNOSTICS repaired_profiles = ROW_COUNT;
  RAISE NOTICE 'Synchronized % profiles with trusted roles in public.profiles', repaired_profiles;

  RAISE NOTICE 'Demo auth repair completed successfully!';
END $$;
