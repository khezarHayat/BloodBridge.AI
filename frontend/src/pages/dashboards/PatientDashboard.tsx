import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  PlusCircle,
  Clock,
  CheckCircle2,
  AlertCircle,
  Building,
  Phone,
  Droplet,
  Users,
  Search,
  XCircle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Bell,
  ShieldCheck,
  MapPin,
  Shield,
  Sparkles,
} from 'lucide-react';
import { BloodGroupBadge } from '../../components/BloodGroupBadge';
import { EmergencyBadge } from '../../components/EmergencyBadge';
import { StatusBadge } from '../../components/StatusBadge';
import { StatsCard } from '../../components/StatsCard';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';
import { BloodGroup, BloodRequest, EmergencyLevel, DonorInvitation, Notification } from '../../types';

export const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';

  const [myRequests, setMyRequests] = useState<BloodRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  // Invitation tracking state
  const [invitationsMap, setInvitationsMap] = useState<Record<string, DonorInvitation[]>>({});
  const [expandedRequests, setExpandedRequests] = useState<Record<string, boolean>>({});
  const [loadingInvitations, setLoadingInvitations] = useState<Record<string, boolean>>({});

  // Notifications state
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loadingNotifications, setLoadingNotifications] = useState(false);

  // Form states
  const [patientName, setPatientName] = useState('');
  const [bloodGroup, setBloodGroup] = useState<BloodGroup>('B+');
  const [unitsNeeded, setUnitsNeeded] = useState(2);
  const [hospitalName, setHospitalName] = useState('Hayatabad Medical Complex (HMC)');
  const [hospitalAddress, setHospitalAddress] = useState('Phase 4, Hayatabad, Peshawar');
  const [area, setArea] = useState('Hayatabad');
  const [emergencyLevel, setEmergencyLevel] = useState<EmergencyLevel>('urgent');
  const [contactName, setContactName] = useState(user?.full_name || '');
  const [contactPhone, setContactPhone] = useState(user?.phone || '');
  const [notes, setNotes] = useState('');

  const bloodGroups: BloodGroup[] = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  const peshawarAreas = [
    'Hayatabad',
    'University Town',
    'Saddar',
    'Gulbahar',
    'Warsak Road',
    'Ring Road',
    'Kohat Road',
    'Charsadda Road',
    'Dalazak Road',
    'Dabgari Gardens',
  ];

  // Canonical Peshawar area coordinates from platform constants
  const peshawarAreaCoordinates: Record<string, { lat: number; lng: number }> = {
    'Hayatabad': { lat: 34.0017, lng: 71.4448 },
    'University Town': { lat: 34.0085, lng: 71.4785 },
    'Saddar': { lat: 34.0253, lng: 71.5784 },
    'Gulbahar': { lat: 34.0312, lng: 71.5656 },
    'Warsak Road': { lat: 34.0620, lng: 71.5120 },
    'Ring Road': { lat: 33.9850, lng: 71.5540 },
    'Kohat Road': { lat: 33.9520, lng: 71.5410 },
    'Dalazak Road': { lat: 34.0410, lng: 71.6020 },
    'Dabgari Gardens': { lat: 34.0080, lng: 71.5620 },
    'Charsadda Road': { lat: 34.0550, lng: 71.5830 },
  };

  // Major hospital locations in Peshawar with verified coordinates
  const commonHospitals = [
    { name: 'Hayatabad Medical Complex (HMC)', address: 'Phase 4, Hayatabad, Peshawar', area: 'Hayatabad', lat: 34.0017, lng: 71.4448 },
    { name: 'Lady Reading Hospital (LRH)', address: 'Soekarno Square, Peshawar City', area: 'Saddar', lat: 34.0253, lng: 71.5784 },
    { name: 'Khyber Teaching Hospital (KTH)', address: 'University Road, Peshawar', area: 'University Town', lat: 34.0085, lng: 71.4785 },
    { name: 'North West General Hospital', address: 'Sector A-3, Phase 5, Hayatabad', area: 'Hayatabad', lat: 33.9940, lng: 71.4359 },
    { name: 'Rehman Medical Institute (RMI)', address: 'Phase 5, Hayatabad, Peshawar', area: 'Hayatabad', lat: 33.9922, lng: 71.4358 },
  ];

  // Safely resolve geolocation from trusted hospital data or area fallback
  const resolveCoordinates = (selectedHospital: string, selectedArea: string): { latitude?: number; longitude?: number } => {
    const trimmed = selectedHospital.trim().toLowerCase();
    if (trimmed) {
      const hospitalMatch = commonHospitals.find(
        (h) =>
          h.name.toLowerCase() === trimmed ||
          trimmed.includes(h.name.toLowerCase()) ||
          h.name.toLowerCase().includes(trimmed)
      );
      if (hospitalMatch) {
        return { latitude: hospitalMatch.lat, longitude: hospitalMatch.lng };
      }
    }

    if (selectedArea && peshawarAreaCoordinates[selectedArea]) {
      const areaCoords = peshawarAreaCoordinates[selectedArea];
      return { latitude: areaCoords.lat, longitude: areaCoords.lng };
    }

    return {};
  };

  useEffect(() => {
    loadMyRequests();
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    setLoadingNotifications(true);
    try {
      const res = await api.getNotifications({ limit: 20 });
      if (res && res.notifications) {
        setNotifications(res.notifications);
      }
    } catch (err) {
      console.error('Error fetching notifications:', err);
    } finally {
      setLoadingNotifications(false);
    }
  };

  const loadMyRequests = async () => {
    setLoading(true);
    try {
      const res = await api.getMyRequests();
      if (res && res.requests) {
        setMyRequests(res.requests);
      }
    } catch (err) {
      console.error('Error fetching requests:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadInvitationsForRequest = async (requestId: string) => {
    setLoadingInvitations((prev) => ({ ...prev, [requestId]: true }));
    try {
      const data = await api.getInvitationsForRequest(requestId);
      setInvitationsMap((prev) => ({ ...prev, [requestId]: data || [] }));
    } catch (err) {
      console.error(`Error fetching invitations for request ${requestId}:`, err);
    } finally {
      setLoadingInvitations((prev) => ({ ...prev, [requestId]: false }));
    }
  };

  const toggleRequestExpanded = (requestId: string) => {
    const isCurrentlyExpanded = !!expandedRequests[requestId];
    setExpandedRequests((prev) => ({ ...prev, [requestId]: !isCurrentlyExpanded }));
    if (!isCurrentlyExpanded && !invitationsMap[requestId]) {
      loadInvitationsForRequest(requestId);
    }
  };

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormError(null);
    setFormSuccess(null);

    try {
      const coords = resolveCoordinates(hospitalName, area);

      const payload: Record<string, any> = {
        patient_name: patientName,
        blood_group: bloodGroup,
        units_needed: Number(unitsNeeded),
        hospital_name: hospitalName,
        hospital_address: hospitalAddress,
        city: 'Peshawar',
        area,
        emergency_level: emergencyLevel,
        contact_name: contactName || user?.full_name || 'Requester',
        contact_phone: contactPhone || '03000000000',
        additional_notes: notes,
        ...(coords.latitude !== undefined && coords.longitude !== undefined
          ? { latitude: coords.latitude, longitude: coords.longitude }
          : {}),
      };

      const res = await api.createBloodRequest(payload);
      setFormSuccess(
        `Blood request ${res.request_number || 'created'} registered successfully! AI matching engine initiated dispatch to compatible donors.`
      );
      // Reset form
      setPatientName('');
      setNotes('');
      await loadMyRequests();
      setSearchParams({ tab: 'requests' });
    } catch (err: any) {
      setFormError(err.message || 'Failed to submit blood request. Please check inputs.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelRequest = async (id: string) => {
    if (!window.confirm('Are you sure you want to cancel this emergency request?')) return;
    try {
      await api.cancelBloodRequest(id, 'Cancelled by requester');
      await loadMyRequests();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel request');
    }
  };

  const activeCount = myRequests.filter((r) => ['pending', 'matching', 'matched'].includes(r.status)).length;
  const fulfilledCount = myRequests.filter((r) => r.status === 'fulfilled').length;
  const totalUnitsNeeded = myRequests.reduce((acc, r) => acc + (r.units_needed || 0), 0);

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-navy">
            Patient &amp; Requester Portal
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage your emergency blood requests and track intelligent donor matching across Peshawar.
          </p>
        </div>
        <button
          onClick={() => setSearchParams({ tab: 'create' })}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-semibold text-sm shadow-sm transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          New Blood Request
        </button>
      </div>

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
          onClick={() => setSearchParams({ tab: 'create' })}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'create'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          Create Request
        </button>
        <button
          onClick={() => setSearchParams({ tab: 'requests' })}
          className={`pb-3 font-semibold transition-colors flex items-center gap-2 ${
            activeTab === 'requests'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          <span>My Requests</span>
          <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded-full font-bold">
            {myRequests.length}
          </span>
        </button>
        <button
          onClick={() => setSearchParams({ tab: 'notifications' })}
          className={`pb-3 font-semibold transition-colors flex items-center gap-2 ${
            activeTab === 'notifications'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          <Bell className="w-4 h-4" />
          <span>Donor Alerts</span>
          {notifications.filter((n) => !n.is_read).length > 0 && (
            <span className="text-[10px] bg-crimson text-white px-1.5 py-0.2 rounded-full font-bold">
              {notifications.filter((n) => !n.is_read).length}
            </span>
          )}
        </button>
      </div>

      {/* TAB CONTENT: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <StatsCard
              title="Active In-Progress Requests"
              value={activeCount}
              subtitle="Matching donors in Peshawar"
              icon={Clock}
              variant="crimson"
            />
            <StatsCard
              title="Fulfilled Transfusions"
              value={fulfilledCount}
              subtitle="Completed blood deliveries"
              icon={CheckCircle2}
              variant="emerald"
            />
            <StatsCard
              title="Total Units Requested"
              value={totalUnitsNeeded}
              subtitle="Pint bags requested across cases"
              icon={Droplet}
              variant="navy"
            />
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-navy text-base">Recent Emergency Requests</h3>
              <button
                onClick={() => setSearchParams({ tab: 'requests' })}
                className="text-xs text-crimson font-semibold hover:underline"
              >
                View all ({myRequests.length}) &gt;
              </button>
            </div>

            {loading ? (
              <p className="text-xs text-slate-500 py-4">Loading your records...</p>
            ) : myRequests.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                No blood requests initiated yet. Click "New Blood Request" to submit one.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {myRequests.slice(0, 3).map((req) => (
                  <div key={req.id} className="py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <BloodGroupBadge bloodGroup={req.blood_group} size="sm" />
                      <div>
                        <p className="text-xs font-bold text-navy">{req.patient_name}</p>
                        <p className="text-[11px] text-slate-500">{req.hospital_name} — {req.area}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <EmergencyBadge level={req.emergency_level} size="sm" />
                      <StatusBadge status={req.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: CREATE REQUEST */}
      {activeTab === 'create' && (
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-subtle max-w-3xl">
          <h2 className="text-xl font-bold text-navy mb-2 flex items-center gap-2">
            <PlusCircle className="w-5 h-5 text-crimson" />
            Submit Emergency Blood Request
          </h2>
          <p className="text-xs text-slate-500 mb-6">
            Submitting this request will automatically invoke the BloodBridge Python matching engine to score, rank, and notify compatible donors in Peshawar.
          </p>

          {formSuccess && (
            <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-600" />
              <span>{formSuccess}</span>
            </div>
          )}

          {formError && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-600" />
              <span>{formError}</span>
            </div>
          )}

          <form onSubmit={handleCreateRequest} className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Patient Full Name</label>
                <input
                  type="text"
                  required
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  placeholder="e.g. Fatima Bibi"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Required Blood Group</label>
                <select
                  value={bloodGroup}
                  onChange={(e) => setBloodGroup(e.target.value as BloodGroup)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                >
                  {bloodGroups.map((bg) => (
                    <option key={bg} value={bg}>{bg}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Units Needed (Bags)</label>
                <input
                  type="number"
                  min={1}
                  max={20}
                  required
                  value={unitsNeeded}
                  onChange={(e) => setUnitsNeeded(Number(e.target.value))}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Urgency Level</label>
                <select
                  value={emergencyLevel}
                  onChange={(e) => setEmergencyLevel(e.target.value as EmergencyLevel)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                >
                  <option value="critical">Critical (Immediate surgery / ICU)</option>
                  <option value="urgent">Urgent (Within 24 hours)</option>
                  <option value="normal">Normal (Scheduled transfusion)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Peshawar Area</label>
                <select
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                >
                  {peshawarAreas.map((a) => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Hospital / Medical Center</label>
              <input
                type="text"
                required
                value={hospitalName}
                onChange={(e) => setHospitalName(e.target.value)}
                placeholder="e.g. Lady Reading Hospital (LRH)"
                className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
              <div className="flex flex-wrap gap-2 mt-2">
                <span className="text-[11px] text-slate-500">Quick select:</span>
                {commonHospitals.map((h) => (
                  <button
                    key={h.name}
                    type="button"
                    onClick={() => {
                      setHospitalName(h.name);
                      setHospitalAddress(h.address);
                      setArea(h.area);
                    }}
                    className="text-[10px] px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700"
                  >
                    {h.name.split('(')[0].trim()}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Hospital Address / Ward Info</label>
              <input
                type="text"
                required
                value={hospitalAddress}
                onChange={(e) => setHospitalAddress(e.target.value)}
                placeholder="e.g. Ward 4, Surgical ICU, LRH Peshawar"
                className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Attendant Contact Name</label>
                <input
                  type="text"
                  required
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  placeholder="e.g. Tariq Afridi"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Attendant Mobile Phone</label>
                <input
                  type="tel"
                  required
                  value={contactPhone}
                  onChange={(e) => setContactPhone(e.target.value)}
                  placeholder="03001234567"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Clinical Notes (Optional)</label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any special medical condition, patient MR number, or urgency details..."
                className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 px-4 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-sm shadow transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isSubmitting ? 'Executing Matching Engine...' : 'Publish Emergency Request'}
            </button>
          </form>
        </div>
      )}

      {/* TAB CONTENT: MY REQUESTS */}
      {activeTab === 'requests' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-navy">
              My Submitted Requests ({myRequests.length})
            </h2>
          </div>

          {loading ? (
            <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
              <p className="text-xs text-slate-500">Loading requests...</p>
            </div>
          ) : myRequests.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
              <Droplet className="w-10 h-10 text-slate-300 mx-auto mb-2" />
              <p className="text-sm font-semibold text-navy">No requests created yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {myRequests.map((req) => (
                <div
                  key={req.id}
                  className="bg-white rounded-xl p-5 border border-slate-200 shadow-subtle space-y-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <BloodGroupBadge bloodGroup={req.blood_group} size="md" />
                      <div>
                        <span className="text-xs font-mono text-slate-400">{req.request_number}</span>
                        <h4 className="font-bold text-navy text-sm">{req.patient_name}</h4>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <EmergencyBadge level={req.emergency_level} size="sm" />
                      <StatusBadge status={req.status} />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs bg-surface p-3 rounded-lg text-slate-600">
                    <div>
                      <span className="text-slate-400 block">Fulfillment:</span>
                      <span className="font-bold text-navy">{req.units_fulfilled} / {req.units_needed} units</span>
                      <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full transition-all"
                          style={{
                            width: `${Math.min(100, Math.round(((req.units_fulfilled || 0) / (req.units_needed || 1)) * 100))}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400 block">Matched Donors:</span>
                      <span className="font-bold text-crimson">
                        {invitationsMap[req.id] ? invitationsMap[req.id].length : (req.matched_donors || 0)} candidates
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-1">
                        {invitationsMap[req.id]
                          ? `${invitationsMap[req.id].filter((i) => i.status === 'accepted').length} accepted`
                          : 'Live dispatch active'}
                      </span>
                    </div>
                    <div className="col-span-2 pt-1 border-t border-slate-200/60 mt-1">
                      <span className="text-slate-400 block">Hospital &amp; Area:</span>
                      <span className="font-medium text-navy">{req.hospital_name} ({req.area})</span>
                    </div>
                  </div>

                  {/* Collapsible Matched Donors & Invitation Tracking Section */}
                  <div className="border-t border-slate-100 pt-3">
                    <button
                      type="button"
                      onClick={() => toggleRequestExpanded(req.id)}
                      className="w-full flex items-center justify-between text-xs font-semibold text-slate-700 hover:text-crimson transition-colors py-1"
                    >
                      <span className="flex items-center gap-1.5">
                        <Users className="w-4 h-4 text-crimson" />
                        <span>Matched Donors &amp; Invitation Tracking</span>
                        {invitationsMap[req.id] && (
                          <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full text-[10px] font-bold">
                            {invitationsMap[req.id].length}
                          </span>
                        )}
                      </span>
                      <span className="flex items-center gap-1 text-[11px] text-slate-500">
                        {expandedRequests[req.id] ? 'Hide' : 'View Donors'}
                        {expandedRequests[req.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </span>
                    </button>

                    {expandedRequests[req.id] && (
                      <div className="mt-3 space-y-3 bg-slate-50/70 p-3.5 rounded-xl border border-slate-200/80">
                        {/* Summary Bar */}
                        <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-slate-200">
                          <div className="flex items-center gap-1.5 text-[11px]">
                            {invitationsMap[req.id] && (
                              <>
                                <span className="px-2 py-0.5 rounded-full bg-emerald-100/80 text-emerald-800 font-bold">
                                  {invitationsMap[req.id].filter((i) => i.status === 'accepted').length} Accepted
                                </span>
                                <span className="px-2 py-0.5 rounded-full bg-amber-100/80 text-amber-800 font-bold">
                                  {invitationsMap[req.id].filter((i) => i.status === 'pending').length} Pending
                                </span>
                                {invitationsMap[req.id].filter((i) => i.status === 'declined').length > 0 && (
                                  <span className="px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-medium">
                                    {invitationsMap[req.id].filter((i) => i.status === 'declined').length} Declined
                                  </span>
                                )}
                              </>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => loadInvitationsForRequest(req.id)}
                            disabled={loadingInvitations[req.id]}
                            className="inline-flex items-center gap-1 text-[11px] text-slate-600 hover:text-crimson font-medium transition-colors"
                            title="Refresh live donor responses"
                          >
                            <RefreshCw className={`w-3.5 h-3.5 ${loadingInvitations[req.id] ? 'animate-spin text-crimson' : ''}`} />
                            <span>Refresh</span>
                          </button>
                        </div>

                        {/* Donor list */}
                        {loadingInvitations[req.id] ? (
                          <div className="py-4 text-center text-xs text-slate-500">
                            Loading donor response records...
                          </div>
                        ) : !invitationsMap[req.id] || invitationsMap[req.id].length === 0 ? (
                          <div className="py-4 text-center text-xs text-slate-500 space-y-1">
                            <Users className="w-6 h-6 text-slate-300 mx-auto" />
                            <p className="font-semibold text-slate-700">No donor invitations issued yet</p>
                            <p className="text-[11px] text-slate-400">
                              The AI matching engine is actively scanning compatible donors in Peshawar.
                            </p>
                          </div>
                        ) : (
                          <div className="space-y-2.5">
                            {invitationsMap[req.id].map((inv) => (
                              <div
                                key={inv.id}
                                className={`p-3 rounded-xl border transition-all ${
                                  inv.status === 'accepted'
                                    ? 'bg-emerald-50/60 border-emerald-200 shadow-xs'
                                    : inv.status === 'declined'
                                    ? 'bg-slate-100/60 border-slate-200 opacity-70'
                                    : 'bg-white border-slate-200 shadow-xs'
                                }`}
                              >
                                <div className="flex items-center justify-between gap-2">
                                  <div className="flex items-center gap-2.5">
                                    <div className="w-8 h-8 rounded-full bg-slate-100 text-navy flex items-center justify-center font-bold text-xs border border-slate-200">
                                      {inv.donor_name ? inv.donor_name.slice(0, 2).toUpperCase() : 'VD'}
                                    </div>
                                    <div>
                                      <div className="flex items-center gap-1.5">
                                        <p className="text-xs font-bold text-navy">
                                          {inv.donor_name || 'Volunteer Donor'}
                                        </p>
                                        <span title="Verified Peshawar Donor">
                                          <ShieldCheck className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                                        </span>
                                        {inv.donor_blood_group && (
                                          <BloodGroupBadge bloodGroup={inv.donor_blood_group} size="sm" />
                                        )}
                                      </div>
                                      <p className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                                        <MapPin className="w-3 h-3 text-slate-400" />
                                        <span>{inv.donor_area || 'Peshawar'}</span>
                                        {inv.distance_km !== undefined && inv.distance_km !== null && (
                                          <span>• {inv.distance_km} km away</span>
                                        )}
                                      </p>
                                    </div>
                                  </div>

                                  <div className="flex flex-col items-end gap-1">
                                    {inv.status === 'accepted' && (
                                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                                        Accepted
                                      </span>
                                    )}
                                    {inv.status === 'pending' && (
                                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800 border border-amber-300">
                                        <Clock className="w-3 h-3 text-amber-600 animate-pulse" />
                                        Pending
                                      </span>
                                    )}
                                    {inv.status === 'declined' && (
                                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-200 text-slate-700">
                                        <XCircle className="w-3 h-3 text-slate-500" />
                                        Declined
                                      </span>
                                    )}

                                    <span className="text-[10px] font-bold text-crimson bg-crimson-50 px-1.5 py-0.5 rounded">
                                      {Math.round(inv.match_score)}% Match
                                    </span>
                                  </div>
                                </div>

                                {/* Match factors */}
                                {inv.match_reasons && inv.match_reasons.length > 0 && (
                                  <div className="flex flex-wrap gap-1 mt-2">
                                    {inv.match_reasons.slice(0, 3).map((reason, idx) => (
                                      <span key={idx} className="text-[10px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                                        {reason}
                                      </span>
                                    ))}
                                  </div>
                                )}

                                {inv.status === 'accepted' && (
                                  <div className="mt-2 p-2 rounded-lg bg-emerald-100 text-emerald-900 text-[11px] flex items-center justify-between">
                                    <span>✓ Donor confirmed donation readiness. Coordinated through hospital ward.</span>
                                    {inv.responded_at && (
                                      <span className="text-[10px] text-emerald-700 font-mono">
                                        {new Date(inv.responded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                      </span>
                                    )}
                                  </div>
                                )}
                              </div>
                            ))}

                            <div className="pt-2 text-center">
                              <p className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                                <Shield className="w-3 h-3 text-slate-400" />
                                Donor phone numbers &amp; personal records are strictly protected under BloodBridge AI privacy protocols.
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {req.status !== 'cancelled' && req.status !== 'fulfilled' && (
                    <div className="pt-2 flex justify-end">
                      <button
                        onClick={() => handleCancelRequest(req.id)}
                        className="text-xs text-red-600 hover:text-red-700 font-semibold flex items-center gap-1"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        Cancel Request
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: NOTIFICATIONS / ALERTS */}
      {activeTab === 'notifications' && (
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-subtle space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-navy flex items-center gap-2">
                <Bell className="w-5 h-5 text-crimson" />
                Emergency Request Updates &amp; Alerts
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Real-time updates regarding donor responses, fulfillment milestones, and clinical dispatches across Peshawar.
              </p>
            </div>
            <button
              onClick={loadNotifications}
              disabled={loadingNotifications}
              className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-crimson font-medium"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingNotifications ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {loadingNotifications ? (
            <p className="text-xs text-slate-500 py-8 text-center">Loading notifications...</p>
          ) : notifications.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              <Bell className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              No alerts received yet. Updates will appear here as donors respond to your requests.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {notifications.map((n) => (
                <div key={n.id} className="py-4 flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                    n.title.toLowerCase().includes('accept')
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-crimson-50 text-crimson'
                  }`}>
                    {n.title.toLowerCase().includes('accept') ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <AlertCircle className="w-4 h-4" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-navy">{n.title}</h4>
                      <span className="text-[10px] text-slate-400">
                        {n.created_at ? new Date(n.created_at).toLocaleString() : ''}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 mt-0.5">{n.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
