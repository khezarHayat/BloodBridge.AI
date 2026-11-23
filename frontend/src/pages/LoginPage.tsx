import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { HeartHandshake, Lock, Mail, AlertCircle, ArrowRight, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const user = await login(email, password);
      redirectByRole(user.role);
    } catch (err: any) {
      setError(err.message || 'Login failed. Invalid credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const DEMO_CREDENTIALS: Record<'patient' | 'donor' | 'blood_bank' | 'admin', { email: string; pass: string }> = {
    admin: { email: 'admin1@bloodbridge.demo', pass: 'DemoPassword123!' },
    donor: { email: 'donor01@bloodbridge.demo', pass: 'DemoPassword123!' },
    blood_bank: { email: 'lrh.bloodbank@bloodbridge.demo', pass: 'DemoPassword123!' },
    patient: { email: 'patient1@bloodbridge.demo', pass: 'DemoPassword123!' },
  };

  const handleQuickDemo = async (demoRole: 'patient' | 'donor' | 'blood_bank' | 'admin') => {
    setError(null);
    setIsSubmitting(true);
    const { email: demoEmail, pass: demoPass } = DEMO_CREDENTIALS[demoRole];

    try {
      const user = await login(demoEmail, demoPass);
      redirectByRole(user.role);
    } catch {
      // If backend mock user fallback is needed
      setEmail(demoEmail);
      setPassword(demoPass);
      setError(`Credentials populated: ${demoEmail}. Click "Sign In" to authenticate.`);
      setIsSubmitting(false);
    }
  };

  const redirectByRole = (role: string) => {
    switch (role) {
      case 'admin':
        navigate('/dashboard/admin');
        break;
      case 'donor':
        navigate('/dashboard/donor');
        break;
      case 'blood_bank':
      case 'hospital':
        navigate('/dashboard/blood-bank');
        break;
      case 'patient':
      default:
        navigate('/dashboard/patient');
        break;
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 sm:p-10 rounded-2xl border border-slate-200 shadow-card">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-crimson flex items-center justify-center text-white mx-auto shadow-sm">
            <HeartHandshake className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-extrabold text-navy">Welcome Back</h2>
          <p className="text-xs text-slate-500">
            Sign in to BloodBridge Emergency Coordination Network
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-50 text-red-700 text-xs flex items-center gap-2 border border-red-200">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@bloodbridge.pk"
                className="w-full pl-9 text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-medium text-slate-700">Password</label>
              <a href="#reset" className="text-[11px] text-crimson hover:underline">
                Forgot?
              </a>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 px-4 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isSubmitting ? 'Verifying...' : 'Sign In'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Switcher */}
        <div className="pt-4 border-t border-slate-100 space-y-2">
          <p className="text-[11px] font-semibold text-slate-500 text-center flex items-center justify-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            Quick Demo Role Test (1-Click Fill)
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickDemo('patient')}
              className="px-2.5 py-1.5 rounded-lg bg-surface hover:bg-slate-200 text-slate-700 font-medium text-center border border-slate-200"
            >
              Patient / Requester
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('donor')}
              className="px-2.5 py-1.5 rounded-lg bg-surface hover:bg-slate-200 text-slate-700 font-medium text-center border border-slate-200"
            >
              Blood Donor
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('blood_bank')}
              className="px-2.5 py-1.5 rounded-lg bg-surface hover:bg-slate-200 text-slate-700 font-medium text-center border border-slate-200"
            >
              Blood Bank Lab
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('admin')}
              className="px-2.5 py-1.5 rounded-lg bg-surface hover:bg-slate-200 text-slate-700 font-medium text-center border border-slate-200"
            >
              Admin Portal
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 pt-2">
          Don't have an account?{' '}
          <Link to="/register" className="text-crimson font-bold hover:underline">
            Register Here
          </Link>
        </p>
      </div>
    </div>
  );
};
