import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Heart,
  CheckCircle2,
  Shield,
  Clock,
  MapPin,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { BloodGroup } from '../types';

export const BecomeDonorPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [bloodGroup, setBloodGroup] = useState<BloodGroup>('O+');
  const [area, setArea] = useState('Hayatabad');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!bloodGroup) {
      setError('Please select a valid blood group.');
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        full_name: fullName,
        email,
        password,
        phone,
        role: 'donor',
        blood_group: bloodGroup,
        city: 'Peshawar',
        area,
      });
      navigate('/dashboard/donor');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check inputs.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-crimson-50 text-crimson text-xs font-semibold mb-4 border border-crimson-200">
          <Heart className="w-3.5 h-3.5" />
          Join Peshawar's Lifesaving Network
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-navy">
          Become a Registered Blood Donor
        </h1>
        <p className="mt-3 text-slate-600 text-base">
          Sign up to be matched with emergency requests at Lady Reading Hospital, Hayatabad Medical Complex, Khyber Teaching Hospital, and local trauma centers.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Donor Registration Form */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle">
          <h2 className="text-xl font-bold text-navy mb-6 flex items-center gap-2">
            <Heart className="w-5 h-5 text-crimson" />
            Volunteer Donor Registration
          </h2>

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Full Legal Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Tariq Khan"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Phone Number (Mobile)</label>
                <input
                  type="tel"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="03001234567"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="tariq@example.com"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Password (min 8 chars)</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>
            </div>

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

            <div className="p-4 rounded-xl bg-surface border border-slate-200 text-xs text-slate-600 space-y-2">
              <div className="flex items-start gap-2">
                <Shield className="w-4 h-4 text-crimson flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Privacy First:</strong> Your phone number is kept confidential. Requesters will only receive contact info after you review and accept an invitation.
                </span>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 px-4 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                'Creating Donor Profile...'
              ) : (
                <>
                  Complete Donor Registration
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <p className="text-center text-xs text-slate-500">
              Already registered?{' '}
              <Link to="/login" className="text-crimson font-semibold hover:underline">
                Sign In to Donor Dashboard
              </Link>
            </p>
          </form>
        </div>

        {/* Eligibility & Info */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-4">
            <h3 className="font-bold text-navy text-base">Eligibility Checklist</h3>
            <ul className="space-y-3 text-xs text-slate-600">
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Age:</strong> Between 18 and 60 years old.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Weight:</strong> At least 50 kg (110 lbs).</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Donation Interval:</strong> At least 56 days since your last whole blood donation.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>General Health:</strong> No active fever, infections, or untreated chronic conditions.</span>
              </li>
            </ul>
          </div>

          <div className="bg-navy rounded-2xl p-6 text-white space-y-3">
            <h3 className="font-bold text-base">Emergency Donors Needed</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Peshawar trauma centers face constant demand for <strong>O-</strong> and <strong>B+</strong> blood due to highway accidents on the Ring Road and elective cardiac surgeries.
            </p>
            <div className="pt-2">
              <span className="text-xs font-semibold text-crimson-300">Lady Reading Hospital • HMC • KTH</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
