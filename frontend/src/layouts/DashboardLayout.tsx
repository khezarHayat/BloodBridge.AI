import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  HeartHandshake,
  Droplet,
  Building2,
  Users,
  Bell,
  LogOut,
  ShieldCheck,
  MapPin,
  ChevronRight,
  Menu,
  X,
  PlusCircle,
  FileText,
  Activity,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getNavItems = () => {
    const role = user?.role || 'patient';

    if (role === 'admin') {
      return [
        { label: 'Admin Overview', path: '/dashboard/admin', icon: LayoutDashboard },
        { label: 'User Verification', path: '/dashboard/admin?tab=users', icon: ShieldCheck },
        { label: 'Blood Requests', path: '/dashboard/admin?tab=requests', icon: Droplet },
        { label: 'Blood Banks', path: '/dashboard/admin?tab=banks', icon: Building2 },
        { label: 'Audit Logs', path: '/dashboard/admin?tab=audit', icon: Activity },
      ];
    }

    if (role === 'donor') {
      return [
        { label: 'Donor Overview', path: '/dashboard/donor', icon: LayoutDashboard },
        { label: 'Emergency Requests', path: '/dashboard/donor?tab=requests', icon: Droplet },
        { label: 'My Invitations', path: '/dashboard/donor?tab=invitations', icon: Bell },
        { label: 'Donation History', path: '/dashboard/donor?tab=history', icon: FileText },
        { label: 'Peshawar Map', path: '/dashboard/donor?tab=map', icon: MapPin },
      ];
    }

    if (role === 'blood_bank' || role === 'hospital') {
      return [
        { label: 'Facility Overview', path: '/dashboard/blood-bank', icon: LayoutDashboard },
        { label: 'Inventory Batches', path: '/dashboard/blood-bank?tab=inventory', icon: Droplet },
        { label: 'Add Stock', path: '/dashboard/blood-bank?tab=add', icon: PlusCircle },
        { label: 'Incoming Requests', path: '/dashboard/blood-bank?tab=requests', icon: Bell },
        { label: 'Facility Profile', path: '/dashboard/blood-bank?tab=profile', icon: Building2 },
      ];
    }

    // Default: Patient / Requester
    return [
      { label: 'Requester Overview', path: '/dashboard/patient', icon: LayoutDashboard },
      { label: 'Create Blood Request', path: '/dashboard/patient?tab=create', icon: PlusCircle },
      { label: 'My Requests', path: '/dashboard/patient?tab=requests', icon: FileText },
      { label: 'Nearby Donors', path: '/dashboard/patient?tab=donors', icon: Users },
      { label: 'Peshawar Blood Banks', path: '/dashboard/patient?tab=banks', icon: Building2 },
    ];
  };

  const navItems = getNavItems();

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar Desktop */}
      <aside className="hidden lg:flex flex-col w-64 bg-navy text-slate-300 border-r border-slate-800">
        <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-crimson flex items-center justify-center text-white">
              <HeartHandshake className="w-5 h-5" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">BloodBridge</span>
          </Link>
        </div>

        {/* User Card */}
        <div className="p-4 mx-3 my-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
          <p className="text-xs text-slate-400 font-medium">Logged in as</p>
          <p className="text-sm font-bold text-white truncate mt-0.5">{user?.full_name || 'Demo User'}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-crimson text-white">
              {user?.role || 'Patient'}
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <MapPin className="w-3 h-3 text-slate-400" />
              {user?.area || 'Peshawar'}
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname + location.search === item.path;
            return (
              <Link
                key={item.label}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-crimson text-white font-semibold'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Logout bottom */}
        <div className="p-4 border-t border-slate-800">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Link to="/" className="hover:text-navy">Home</Link>
              <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              <span className="font-semibold text-navy capitalize">{user?.role || 'Dashboard'}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full border border-emerald-200 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Peshawar Network Active
            </span>
            <button
              onClick={handleLogout}
              className="p-2 text-slate-500 hover:text-crimson hover:bg-red-50 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Dynamic Outlet */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
