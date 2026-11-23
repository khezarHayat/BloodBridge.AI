import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Droplet,
  Search,
  Filter,
  MapPin,
  Clock,
  Building,
  PlusCircle,
  Phone,
  AlertTriangle,
} from 'lucide-react';
import { BloodGroupBadge } from '../components/BloodGroupBadge';
import { EmergencyBadge } from '../components/EmergencyBadge';
import { StatusBadge } from '../components/StatusBadge';
import { Map, MapMarkerItem } from '../components/Map';
import { api } from '../services/api';
import { BloodGroup, BloodRequest, EmergencyLevel } from '../types';

export const FindBloodPage: React.FC = () => {
  const [requests, setRequests] = useState<BloodRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedGroup, setSelectedGroup] = useState<string>('');
  const [selectedArea, setSelectedArea] = useState<string>('');
  const [selectedEmergency, setSelectedEmergency] = useState<string>('');

  const bloodGroups: BloodGroup[] = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
  const areas = [
    'All Areas',
    'Hayatabad',
    'University Town',
    'Saddar',
    'Gulbahar',
    'Warsak Road',
    'Ring Road',
    'Kohat Road',
  ];

  useEffect(() => {
    fetchRequests();
  }, [selectedGroup, selectedArea, selectedEmergency]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (selectedGroup) params.blood_group = selectedGroup;
      if (selectedArea && selectedArea !== 'All Areas') params.area = selectedArea;
      if (selectedEmergency) params.emergency_level = selectedEmergency;

      const res = await api.getBloodRequests(params);
      if (res && res.requests) {
        setRequests(res.requests);
      }
    } catch (err) {
      console.error('Failed to load blood requests:', err);
    } finally {
      setLoading(false);
    }
  };

  // Prepare map markers
  const mapMarkers: MapMarkerItem[] = requests
    .filter((r) => r.latitude && r.longitude)
    .map((r) => ({
      id: r.id,
      lat: r.latitude!,
      lng: r.longitude!,
      title: `${r.units_needed} Unit(s) ${r.blood_group} - ${r.patient_name}`,
      subtitle: `${r.hospital_name}, ${r.area}`,
      type: 'request',
      bloodGroup: r.blood_group,
      phone: r.contact_phone,
    }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-bold text-crimson tracking-wider">
            Emergency Dispatch
          </span>
          <h1 className="text-3xl font-extrabold text-navy mt-1">Active Blood Requests — Peshawar</h1>
          <p className="text-slate-600 text-sm mt-1">
            Real-time emergency blood requests verified across Peshawar hospitals and clinics.
          </p>
        </div>

        <Link
          to="/dashboard/patient?tab=create"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-semibold shadow-sm transition-all text-sm self-start md:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          Create Blood Request
        </Link>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-subtle space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
          <Filter className="w-3.5 h-3.5 text-crimson" />
          Filter Requests
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Blood group pills */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1.5">Blood Group</label>
            <select
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
              className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
            >
              <option value="">All Blood Groups</option>
              {bloodGroups.map((bg) => (
                <option key={bg} value={bg}>{bg}</option>
              ))}
            </select>
          </div>

          {/* Area filter */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1.5">Peshawar Area</label>
            <select
              value={selectedArea}
              onChange={(e) => setSelectedArea(e.target.value)}
              className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
            >
              {areas.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>

          {/* Emergency urgency */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1.5">Urgency Level</label>
            <select
              value={selectedEmergency}
              onChange={(e) => setSelectedEmergency(e.target.value)}
              className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
            >
              <option value="">All Urgency Levels</option>
              <option value="critical">Critical (Immediate)</option>
              <option value="urgent">Urgent (&lt; 24h)</option>
              <option value="normal">Normal (Scheduled)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Interactive Map */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-subtle space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-navy text-sm flex items-center gap-2">
            <MapPin className="w-4 h-4 text-crimson" />
            Peshawar Geographical Distribution
          </h3>
          <span className="text-xs text-slate-500">
            {mapMarkers.length} geocoded locations
          </span>
        </div>
        <Map markers={mapMarkers} height="360px" />
      </div>

      {/* Request List Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-navy">
            {loading ? 'Searching...' : `Found ${requests.length} Blood Request(s)`}
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
            <div className="w-8 h-8 border-4 border-crimson border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-slate-500">Querying BloodBridge network...</p>
          </div>
        ) : requests.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200 p-8">
            <Droplet className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-bold text-navy">No Matching Blood Requests Found</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
              There are currently no open blood requests matching the selected filters in Peshawar.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {requests.map((req) => (
              <div
                key={req.id}
                className="bg-white rounded-xl p-5 border border-slate-200 shadow-subtle hover:shadow-card transition-all space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <BloodGroupBadge bloodGroup={req.blood_group} size="lg" />
                    <div>
                      <p className="text-xs text-slate-500 font-mono">{req.request_number}</p>
                      <h4 className="font-bold text-navy text-base">{req.patient_name}</h4>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5">
                    <EmergencyBadge level={req.emergency_level} />
                    <StatusBadge status={req.status} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 bg-surface rounded-lg p-3">
                  <div>
                    <span className="text-slate-400 block">Units Needed:</span>
                    <span className="font-bold text-navy">{req.units_needed} Bag(s)</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Fulfilled:</span>
                    <span className="font-bold text-navy">{req.units_fulfilled} Unit(s)</span>
                  </div>
                  <div className="col-span-2 pt-1">
                    <span className="text-slate-400 block">Hospital & Location:</span>
                    <span className="font-semibold text-navy flex items-center gap-1 mt-0.5">
                      <Building className="w-3.5 h-3.5 text-crimson" />
                      {req.hospital_name} — {req.area}, {req.city}
                    </span>
                  </div>
                </div>

                {req.additional_notes && (
                  <p className="text-xs text-slate-500 italic">
                    "{req.additional_notes}"
                  </p>
                )}

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    {req.contact_name}: {req.contact_phone}
                  </span>
                  <Link
                    to={`/dashboard/donor?tab=invitations`}
                    className="text-crimson font-bold hover:underline"
                  >
                    Respond &gt;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
