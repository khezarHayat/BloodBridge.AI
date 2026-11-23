export type BloodGroup = 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-';
export type UserRole = 'patient' | 'donor' | 'blood_bank' | 'hospital' | 'admin';
export type EmergencyLevel = 'critical' | 'urgent' | 'normal';
export type RequestStatus = 'pending' | 'matching' | 'matched' | 'donor_confirmed' | 'fulfilled' | 'cancelled' | 'expired';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  city?: string;
  district?: string;
  area?: string;
  address?: string;
  avatar_url?: string;
  is_verified: boolean;
  is_active: boolean;
  created_at?: string;
}

export interface Donor {
  id: string;
  user_id: string;
  full_name: string;
  blood_group: BloodGroup;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  weight?: number;
  last_donation_date?: string;
  total_donations: number;
  is_available: boolean;
  availability_radius_km?: number;
  consent_notifications?: boolean;
  medical_conditions?: string;
  is_eligible?: boolean;
  is_verified?: boolean;
  city?: string;
  area?: string;
  distance_km?: number;
  created_at?: string;
}

export interface BloodRequest {
  id: string;
  request_number: string;
  requester_id: string;
  requester_name?: string;
  patient_name: string;
  blood_group: BloodGroup;
  units_needed: number;
  units_fulfilled: number;
  hospital_name: string;
  hospital_address: string;
  city: string;
  area: string;
  latitude?: number;
  longitude?: number;
  emergency_level: EmergencyLevel;
  required_by?: string;
  contact_name: string;
  contact_phone: string;
  additional_notes?: string;
  status: RequestStatus;
  matched_donors?: number;
  created_at?: string;
  updated_at?: string;
}

export interface BloodBank {
  id: string;
  user_id: string;
  name: string;
  license_number: string;
  type: 'government' | 'private' | 'hospital' | 'ngo';
  phone: string;
  email?: string;
  address: string;
  city: string;
  area: string;
  latitude?: number;
  longitude?: number;
  operating_hours?: string;
  is_verified: boolean;
  is_active: boolean;
  created_at?: string;
}

export interface InventoryBatch {
  id: string;
  blood_bank_id: string;
  blood_group: BloodGroup;
  units_available: number;
  collection_date: string;
  expiry_date: string;
  screening_status: 'pending' | 'cleared' | 'rejected' | 'quarantined';
  availability_status: 'available' | 'reserved' | 'used' | 'expired' | 'quarantined';
  batch_number?: string;
  notes?: string;
  created_at?: string;
}

export interface InventorySummary {
  blood_group: BloodGroup;
  total_units: number;
  available_units: number;
}

export interface DonorInvitation {
  id: string;
  request_id: string;
  donor_id: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired' | 'cancelled';
  match_score: number;
  match_reasons?: string[];
  distance_km?: number;
  invited_at: string;
  responded_at?: string;
  response_notes?: string;
  request_data?: Partial<BloodRequest>;
  donor_name?: string;
  donor_blood_group?: BloodGroup;
  donor_area?: string;
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: 'invitation' | 'request_update' | 'verification' | 'system' | 'reminder';
  reference_type?: string;
  reference_id?: string;
  is_read: boolean;
  created_at: string;
}

export interface PublicStats {
  registered_donors: number;
  lives_impacted: number;
  fulfilled_requests: number;
  verified_blood_banks: number;
  active_emergency_requests: number;
  district: string;
}

export interface DashboardStats {
  total_users: number;
  total_donors: number;
  verified_donors: number;
  active_requests: number;
  completed_requests: number;
  registered_blood_banks: number;
  pending_verifications: number;
}
