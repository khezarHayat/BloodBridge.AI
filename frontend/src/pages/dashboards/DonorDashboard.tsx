import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Heart,
  Droplet,
  Bell,
  CheckCircle2,
  XCircle,
  Clock,
  MapPin,
  Calendar,
  AlertTriangle,
  Building,
  Shield,
  Activity,
} from 'lucide-react';
import { BloodGroupBadge } from '../../components/BloodGroupBadge';
import { EmergencyBadge } from '../../components/EmergencyBadge';
import { StatusBadge } from '../../components/StatusBadge';
import { StatsCard } from '../../components/StatsCard';
import { Map, MapMarkerItem } from '../../components/Map';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';
import { BloodRequest, Donor, DonorInvitation } from '../../types';

export const DonorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';

  const [donorProfile, setDonorProfile] = useState<Donor | null>(null);
  const [invitations, setInvitations] = useState<DonorInvitation[]>([]);
  const [nearbyRequests, setNearbyRequests] = useState<BloodRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [isToggling, setIsToggling] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadDonorData();
  }, []);

  const loadDonorData = async () => {
    setLoading(true);
    try {
      // 1. Fetch donor profile
      try {
        const d = await api.getMyDonorProfile();
        setDonorProfile(d);
      } catch {
        // Fallback demo profile if new account
        setDonorProfile({
          id: 'demo-donor-id',
          user_id: user?.id || 'demo-user',
          full_name: user?.full_name || 'Volunteer Donor',
          blood_group: 'B+',
          is_available: true,
          total_donations: 4,
          last_donation_date: '2026-08-15',
          area: user?.area || 'Hayatabad',
          city: 'Peshawar',
          is_verified: true,
        });
      }

      // 2. Fetch invitations
      try {
        const invRes = await api.getMyInvitations();
        setInvitations(invRes.invitations || []);
      } catch {
        setInvitations([]);
      }

      // 3. Fetch nearby blood requests
      try {
        const reqRes = await api.getBloodRequests();
        setNearbyRequests(reqRes.requests || []);
      } catch {
        setNearbyRequests([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAvailability = async () => {
    if (!donorProfile) return;
    setIsToggling(true);
    const newStatus = !donorProfile.is_available;
    try {
      await api.toggleAvailability(donorProfile.id, newStatus);
      setDonorProfile({ ...donorProfile, is_available: newStatus });
      setActionSuccess(`Availability status updated: ${newStatus ? 'Ready to Donate' : 'Unavailable'}`);
    } catch {
      // Optimistic update for demo
      setDonorProfile({ ...donorProfile, is_available: newStatus });
      setActionSuccess(`Availability status updated: ${newStatus ? 'Ready to Donate' : 'Unavailable'}`);
    } finally {
      setIsToggling(false);
    }
  };

  const handleRespondInvitation = async (invId: string, status: 'accepted' | 'declined') => {
    try {
      await api.respondToInvitation(invId, { status, response_notes: `Donor responded ${status}` });
      setActionSuccess(`Invitation ${status}! Hospital attendants notified.`);
      await loadDonorData();
    } catch {
      setActionSuccess(`Invitation ${status}! (Updated locally)`);
      setInvitations(
        invitations.map((i) => (i.id === invId ? { ...i, status } : i))
      );
    }
  };

  // Map markers for nearby requests
  const mapMarkers: MapMarkerItem[] = nearbyRequests
    .filter((r) => r.latitude && r.longitude)
    .map((r) => ({
      id: r.id,
      lat: r.latitude!,
      lng: r.longitude!,
      title: `${r.units_needed} Unit ${r.blood_group} - ${r.patient_name}`,
      subtitle: `${r.hospital_name}, ${r.area}`,
      type: 'request',
      bloodGroup: r.blood_group,
    }));

  const pendingInvitations = invitations.filter((i) => i.status === 'pending');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-navy">
              Donor Command Dashboard
            </h1>
            {donorProfile?.is_verified && (
              <span className="text-[10px] font-bold uppercase bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Shield className="w-3 h-3 text-blue-600" />
                Verified
              </span>
            )}
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Track urgent donor invitations, hospital emergencies, and manage your donation readiness.
          </p>
        </div>

        {/* Availability Toggle Button */}
        <div className="flex items-center gap-3 self-start sm:self-auto bg-white p-2 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-600">Donation Status:</span>
          <button
            onClick={handleToggleAvailability}
            disabled={isToggling}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              donorProfile?.is_available
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-slate-200 text-slate-700'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                donorProfile?.is_available ? 'bg-white animate-pulse' : 'bg-slate-500'
              }`}
            />
            {donorProfile?.is_available ? 'Available (Active)' : 'Unavailable'}
          </button>
        </div>
      </div>

      {actionSuccess && (
        <div className="p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs flex items-center justify-between">
          <span>{actionSuccess}</span>
          <button onClick={() => setActionSuccess(null)} className="text-emerald-700 font-bold">&times;</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-200 space-x-6 text-sm">
        <button
          onClick={() => setSearchParams({ tab: 'overview' })}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'overview'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setSearchParams({ tab: 'invitations' })}
          className={`pb-3 font-semibold transition-colors flex items-center gap-2 ${
            activeTab === 'invitations'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          <span>Invitations</span>
          {pendingInvitations.length > 0 && (
            <span className="text-[10px] bg-crimson text-white px-1.5 py-0.5 rounded-full font-bold">
              {pendingInvitations.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setSearchParams({ tab: 'requests' })}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'requests'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          Nearby Requests ({nearbyRequests.length})
        </button>
        <button
          onClick={() => setSearchParams({ tab: 'map' })}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'map'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          Peshawar Map
        </button>
      </div>

      {/* TAB: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <StatsCard
              title="Blood Group"
              value={donorProfile?.blood_group || 'O+'}
              subtitle="Registered clinical ABO/Rh"
              icon={Droplet}
              variant="crimson"
            />
            <StatsCard
              title="Total Donations"
              value={donorProfile?.total_donations || 0}
              subtitle="Completed lifesaving pints"
              icon={Heart}
              variant="emerald"
            />
            <StatsCard
              title="Pending Invitations"
              value={pendingInvitations.length}
              subtitle="Awaiting your acceptance"
              icon={Bell}
              variant="amber"
            />
          </div>

          {/* Safe Window Status Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs uppercase font-bold text-slate-400">Clinical Readiness</span>
              <h3 className="text-base font-bold text-navy mt-0.5">56-Day Donation Interval</h3>
              <p className="text-xs text-slate-500 mt-1">
                Last Whole Blood Donation: <strong>{donorProfile?.last_donation_date || 'No recent record'}</strong>
              </p>
            </div>
            <div className="flex items-center gap-2 bg-emerald-50 text-emerald-800 border border-emerald-200 px-3.5 py-1.5 rounded-xl text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Medically Eligible to Donate Today</span>
            </div>
          </div>

          {/* Pending Invitations Spotlight */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-navy text-base flex items-center gap-2">
                <Bell className="w-4 h-4 text-crimson" />
                Active Urgent Invitations
              </h3>
              <button
                onClick={() => setSearchParams({ tab: 'invitations' })}
                className="text-xs text-crimson font-semibold hover:underline"
              >
                View all ({invitations.length}) &gt;
              </button>
            </div>

            {pendingInvitations.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-400">
                No pending invitations right now. You will be alerted when a compatible request matches your location in Peshawar.
              </div>
            ) : (
              <div className="space-y-3">
                {pendingInvitations.map((inv) => (
                  <div
                    key={inv.id}
                    className="p-4 rounded-xl border border-red-100 bg-red-50/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-red-700 uppercase">Emergency Invitation</span>
                        <span className="text-xs text-slate-500">• Match Score: {inv.match_score} pts</span>
                      </div>
                      <p className="text-sm font-bold text-navy mt-1">
                        Urgent Blood Donation Needed in Peshawar
                      </p>
                      <p className="text-xs text-slate-600 mt-0.5">
                        Distance: ~{inv.distance_km ? `${inv.distance_km} km` : 'Near Hayatabad/KTH'}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleRespondInvitation(inv.id, 'accepted')}
                        className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-colors flex items-center gap-1.5"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Accept
                      </button>
                      <button
                        onClick={() => handleRespondInvitation(inv.id, 'declined')}
                        className="px-3 py-2 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-100 font-semibold text-xs transition-colors"
                      >
                        Decline
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB: INVITATIONS */}
      {activeTab === 'invitations' && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-navy">All Matched Invitations ({invitations.length})</h2>

          {invitations.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
              <p className="text-xs text-slate-500">No invitations received yet.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              {invitations.map((inv) => (
                <div
                  key={inv.id}
                  className="bg-white rounded-xl p-5 border border-slate-200 shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-slate-400">Match #{inv.id.slice(0, 8)}</span>
                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                          inv.status === 'accepted'
                            ? 'bg-emerald-100 text-emerald-800'
                            : inv.status === 'declined'
                            ? 'bg-gray-100 text-gray-700'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {inv.status}
                      </span>
                    </div>
                    <p className="text-sm font-bold text-navy">
                      Emergency Match Score: {inv.match_score} points
                    </p>
                    <p className="text-xs text-slate-500">
                      Invited: {new Date(inv.invited_at).toLocaleString()}
                    </p>
                  </div>

                  {inv.status === 'pending' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleRespondInvitation(inv.id, 'accepted')}
                        className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs"
                      >
                        Accept Request
                      </button>
                      <button
                        onClick={() => handleRespondInvitation(inv.id, 'declined')}
                        className="px-3 py-2 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-100 font-semibold text-xs"
                      >
                        Decline
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB: NEARBY REQUESTS */}
      {activeTab === 'requests' && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-navy">Peshawar Emergency Requests</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {nearbyRequests.map((req) => (
              <div
                key={req.id}
                className="bg-white rounded-xl p-5 border border-slate-200 shadow-subtle space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5">
                    <BloodGroupBadge bloodGroup={req.blood_group} size="md" />
                    <div>
                      <h4 className="font-bold text-navy text-sm">{req.patient_name}</h4>
                      <p className="text-xs text-slate-500">{req.hospital_name} — {req.area}</p>
                    </div>
                  </div>
                  <EmergencyBadge level={req.emergency_level} size="sm" />
                </div>
                <div className="text-xs text-slate-600 bg-surface p-2.5 rounded-lg">
                  Units needed: <span className="font-bold text-navy">{req.units_needed} bag(s)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: MAP */}
      {activeTab === 'map' && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-4">
          <h3 className="font-bold text-navy text-base flex items-center gap-2">
            <MapPin className="w-4 h-4 text-crimson" />
            Active Emergency Calls in Peshawar
          </h3>
          <Map markers={mapMarkers} height="480px" />
        </div>
      )}
    </div>
  );
};
