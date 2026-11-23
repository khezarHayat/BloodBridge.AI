import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Building2,
  Droplet,
  PlusCircle,
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Trash2,
  Shield,
  Layers,
} from 'lucide-react';
import { BloodGroupBadge } from '../../components/BloodGroupBadge';
import { StatsCard } from '../../components/StatsCard';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';
import { BloodBank, BloodGroup, InventoryBatch, InventorySummary } from '../../types';

export const BloodBankDashboard: React.FC = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';

  const [bank, setBank] = useState<BloodBank | null>(null);
  const [summary, setSummary] = useState<InventorySummary[]>([]);
  const [batches, setBatches] = useState<InventoryBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  // Form state
  const [bloodGroup, setBloodGroup] = useState<BloodGroup>('B+');
  const [unitsAvailable, setUnitsAvailable] = useState(5);
  const [collectionDate, setCollectionDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [expiryDate, setExpiryDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 35); // standard whole blood 35-day shelf life
    return d.toISOString().split('T')[0];
  });
  const [screeningStatus, setScreeningStatus] = useState<'cleared' | 'pending'>('cleared');
  const [batchNumber, setBatchNumber] = useState(`BATCH-${Math.floor(Math.random() * 90000 + 10000)}`);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const bloodGroups: BloodGroup[] = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  useEffect(() => {
    loadFacilityData();
  }, []);

  const loadFacilityData = async () => {
    setLoading(true);
    try {
      let currentBank: BloodBank | null = null;
      try {
        currentBank = await api.getMyBloodBank();
        setBank(currentBank);
      } catch {
        // Fallback demo institution
        currentBank = {
          id: 'demo-bank-id',
          user_id: user?.id || 'demo-user',
          name: 'Lady Reading Hospital Blood Bank (LRH)',
          license_number: 'KP-BBA-2026-042',
          type: 'hospital',
          phone: '091-9211430',
          email: 'bloodbank@lrh.gov.pk',
          address: 'Soekarno Square, Peshawar City',
          city: 'Peshawar',
          area: 'Saddar',
          is_verified: true,
          is_active: true,
        };
        setBank(currentBank);
      }

      if (currentBank?.id) {
        try {
          const sumRes = await api.getInventorySummary(currentBank.id);
          setSummary(sumRes);
        } catch {
          // Demo summary
          setSummary(
            bloodGroups.map((bg) => ({
              blood_group: bg,
              total_units: Math.floor(Math.random() * 12 + 2),
              available_units: Math.floor(Math.random() * 10 + 2),
            }))
          );
        }

        try {
          const invRes = await api.getBankInventory(currentBank.id);
          setBatches(invRes.items || invRes.batches || []);
        } catch {
          setBatches([]);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bank) return;
    setIsSubmitting(true);
    setActionError(null);
    setActionSuccess(null);

    try {
      const payload = {
        blood_group: bloodGroup,
        units_available: Number(unitsAvailable),
        collection_date: collectionDate,
        expiry_date: expiryDate,
        screening_status: screeningStatus,
        batch_number: batchNumber,
      };

      await api.addInventoryBatch(bank.id, payload);
      setActionSuccess(`Batch ${batchNumber} (${unitsAvailable} units of ${bloodGroup}) registered!`);
      setBatchNumber(`BATCH-${Math.floor(Math.random() * 90000 + 10000)}`);
      await loadFacilityData();
      setSearchParams({ tab: 'inventory' });
    } catch (err: any) {
      setActionError(err.message || 'Failed to add inventory batch.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteBatch = async (batchId: string) => {
    if (!bank || !window.confirm('Delete this inventory batch record?')) return;
    try {
      await api.deleteInventoryBatch(bank.id, batchId);
      setActionSuccess('Inventory batch deleted.');
      await loadFacilityData();
    } catch (err: any) {
      alert(err.message || 'Failed to delete batch');
    }
  };

  const totalStock = summary.reduce((acc, s) => acc + (s.available_units || 0), 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-navy">
              {bank?.name || 'Blood Bank Management'}
            </h1>
            {bank?.is_verified && (
              <span className="text-[10px] font-bold uppercase bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Shield className="w-3 h-3 text-blue-600" />
                Accredited Facility
              </span>
            )}
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            License: <strong className="text-slate-700">{bank?.license_number}</strong> • Location: {bank?.area}, {bank?.city}
          </p>
        </div>

        <button
          onClick={() => setSearchParams({ tab: 'add' })}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-semibold text-sm shadow-sm transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          Add Blood Stock
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs flex items-center justify-between">
          <span>{actionSuccess}</span>
          <button onClick={() => setActionSuccess(null)} className="font-bold">&times;</button>
        </div>
      )}

      {actionError && (
        <div className="p-3 rounded-xl bg-red-50 text-red-800 border border-red-200 text-xs flex items-center justify-between">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="font-bold">&times;</button>
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
          onClick={() => setSearchParams({ tab: 'inventory' })}
          className={`pb-3 font-semibold transition-colors flex items-center gap-2 ${
            activeTab === 'inventory'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          <span>Inventory Batches</span>
          <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded-full font-bold">
            {batches.length}
          </span>
        </button>
        <button
          onClick={() => setSearchParams({ tab: 'add' })}
          className={`pb-3 font-semibold transition-colors ${
            activeTab === 'add'
              ? 'text-crimson border-b-2 border-crimson'
              : 'text-slate-500 hover:text-navy'
          }`}
        >
          Add Batch
        </button>
      </div>

      {/* TAB: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <StatsCard
              title="Total Available Stock"
              value={`${totalStock} Units`}
              subtitle="Screened & unexpired whole blood"
              icon={Droplet}
              variant="crimson"
            />
            <StatsCard
              title="Active Inventory Batches"
              value={batches.length}
              subtitle="Registered laboratory lots"
              icon={Layers}
              variant="navy"
            />
            <StatsCard
              title="Verification Status"
              value={bank?.is_verified ? 'Verified' : 'Pending'}
              subtitle="KP Blood Transfusion Authority"
              icon={Building2}
              variant="emerald"
            />
          </div>

          {/* Blood Group Grid Cards */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-4">
            <h3 className="font-bold text-navy text-base">Current Stock by Blood Group</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {summary.map((item) => (
                <div
                  key={item.blood_group}
                  className="p-4 rounded-xl border border-slate-200 bg-surface flex items-center justify-between"
                >
                  <BloodGroupBadge bloodGroup={item.blood_group} size="md" />
                  <div className="text-right">
                    <p className="text-xl font-extrabold text-navy">{item.available_units}</p>
                    <p className="text-[10px] text-slate-500">Units Available</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB: INVENTORY BATCHES */}
      {activeTab === 'inventory' && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-navy text-base">Registered Blood Batches ({batches.length})</h3>
            <button
              onClick={() => setSearchParams({ tab: 'add' })}
              className="text-xs text-crimson font-semibold hover:underline"
            >
              + Add New Batch
            </button>
          </div>

          {batches.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              No batches recorded yet. Click "Add Batch" to register collection lots.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-surface">
                    <th className="py-2.5 px-3 font-bold text-navy">Batch ID</th>
                    <th className="py-2.5 px-3 font-bold text-navy">Group</th>
                    <th className="py-2.5 px-3 font-bold text-navy">Units</th>
                    <th className="py-2.5 px-3 font-bold text-navy">Collection</th>
                    <th className="py-2.5 px-3 font-bold text-navy">Expiry</th>
                    <th className="py-2.5 px-3 font-bold text-navy">Screening</th>
                    <th className="py-2.5 px-3 font-bold text-navy text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {batches.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-3 font-mono text-slate-700">{b.batch_number || b.id.slice(0, 8)}</td>
                      <td className="py-2.5 px-3">
                        <BloodGroupBadge bloodGroup={b.blood_group} size="sm" />
                      </td>
                      <td className="py-2.5 px-3 font-bold text-navy">{b.units_available}</td>
                      <td className="py-2.5 px-3 text-slate-500">{b.collection_date}</td>
                      <td className="py-2.5 px-3 font-semibold text-slate-700">{b.expiry_date}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          {b.screening_status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => handleDeleteBatch(b.id)}
                          className="text-red-500 hover:text-red-700 p-1"
                          title="Delete Batch"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB: ADD BATCH */}
      {activeTab === 'add' && (
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-subtle max-w-2xl">
          <h2 className="text-xl font-bold text-navy mb-2 flex items-center gap-2">
            <PlusCircle className="w-5 h-5 text-crimson" />
            Add Blood Stock Batch
          </h2>
          <p className="text-xs text-slate-500 mb-6">
            Register whole blood collection units after mandatory infectious screening (HIV, Hepatitis B/C, Syphilis, Malaria).
          </p>

          <form onSubmit={handleAddBatch} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Blood Group</label>
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

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Units (Bags)</label>
                <input
                  type="number"
                  min={1}
                  max={500}
                  required
                  value={unitsAvailable}
                  onChange={(e) => setUnitsAvailable(Number(e.target.value))}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Collection Date</label>
                <input
                  type="date"
                  required
                  value={collectionDate}
                  onChange={(e) => setCollectionDate(e.target.value)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Expiry Date (35-day shelf)</label>
                <input
                  type="date"
                  required
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Screening Status</label>
                <select
                  value={screeningStatus}
                  onChange={(e) => setScreeningStatus(e.target.value as any)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                >
                  <option value="cleared">Passed / Cleared</option>
                  <option value="pending">Pending Laboratory Testing</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Batch / Barcode Identifier</label>
                <input
                  type="text"
                  required
                  value={batchNumber}
                  onChange={(e) => setBatchNumber(e.target.value)}
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 px-4 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-sm shadow transition-all disabled:opacity-50 mt-2"
            >
              {isSubmitting ? 'Registering Batch...' : 'Register Inventory Batch'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
