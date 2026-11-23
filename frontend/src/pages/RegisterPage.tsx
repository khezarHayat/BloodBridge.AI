import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  HeartHandshake,
  User,
  Heart,
  Building2,
  Shield,
  ArrowRight,
  AlertCircle,
  Droplet,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { BloodGroup, UserRole } from '../types';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [role, setRole] = useState<UserRole>('patient');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
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
    'Dabgari Gardens',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (role === 'donor' && !bloodGroup) {
      setError('Please select your blood group to register as a donor.');
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await register({
        full_name: fullName,
        email,
        password,
        phone,
        role,
        ...(role === 'donor' ? { blood_group: bloodGroup } : {}),
        city: 'Peshawar',
        area,
      });

      if (role === 'admin') navigate('/dashboard/admin');
      else if (role === 'donor') navigate('/dashboard/donor');
      else if (role === 'blood_bank' || role === 'hospital') navigate('/dashboard/blood-bank');
      else navigate('/dashboard/patient');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check your details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full space-y-8 bg-white p-8 sm:p-10 rounded-2xl border border-slate-200 shadow-card">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-crimson flex items-center justify-center text-white mx-auto shadow-sm">
            <HeartHandshake className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-extrabold text-navy">Join BloodBridge Peshawar</h2>
          <p className="text-xs text-slate-500">
            Create an account to request blood, donate, or manage hospital inventory.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-50 text-red-700 text-xs flex items-center gap-2 border border-red-200">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Role Selector Tabs */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-2">Select Your Role</label>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setRole('patient')}
              className={`p-3 rounded-xl border text-center transition-all ${
                role === 'patient'
                  ? 'border-crimson bg-crimson-50/50 text-crimson font-bold shadow-sm'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <User className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs block">Patient</span>
            </button>

            <button
              type="button"
              onClick={() => setRole('donor')}
              className={`p-3 rounded-xl border text-center transition-all ${
                role === 'donor'
                  ? 'border-crimson bg-crimson-50/50 text-crimson font-bold shadow-sm'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Heart className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs block">Donor</span>
            </button>

            <button
              type="button"
              onClick={() => setRole('blood_bank')}
              className={`p-3 rounded-xl border text-center transition-all ${
                role === 'blood_bank'
                  ? 'border-crimson bg-crimson-50/50 text-crimson font-bold shadow-sm'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Building2 className="w-5 h-5 mx-auto mb-1" />
              <span className="text-xs block">Blood Bank</span>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Full Legal Name</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Asad Ullah Khan"
              className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="asad@example.com"
                className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Mobile Phone</label>
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
              <label className="block text-xs font-medium text-slate-700 mb-1">Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min. 8 characters"
                className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
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

          {role === 'donor' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                <Droplet className="w-3.5 h-3.5 text-crimson" />
                Blood Group <span className="text-crimson font-bold">*</span>
              </label>
              <select
                required
                value={bloodGroup}
                onChange={(e) => setBloodGroup(e.target.value as BloodGroup)}
                className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              >
                {bloodGroups.map((bg) => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
              <p className="text-[11px] text-slate-500 mt-1">
                Required for clinical compatibility matching with emergency patient requests.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 px-4 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
          >
            {isSubmitting ? 'Registering...' : `Create ${role.replace('_', ' ')} Account`}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-xs text-slate-500">
          Already registered?{' '}
          <Link to="/login" className="text-crimson font-bold hover:underline">
            Sign In Here
          </Link>
        </p>
      </div>
    </div>
  );
};
