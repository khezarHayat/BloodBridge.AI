import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { MainLayout } from './layouts/MainLayout';
import { DashboardLayout } from './layouts/DashboardLayout';

import { HomePage } from './pages/HomePage';
import { AboutPage } from './pages/AboutPage';
import { HowItWorksPage } from './pages/HowItWorksPage';
import { FindBloodPage } from './pages/FindBloodPage';
import { BecomeDonorPage } from './pages/BecomeDonorPage';
import { ContactPage } from './pages/ContactPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

import { PatientDashboard } from './pages/dashboards/PatientDashboard';
import { DonorDashboard } from './pages/dashboards/DonorDashboard';
import { BloodBankDashboard } from './pages/dashboards/BloodBankDashboard';
import { AdminDashboard } from './pages/dashboards/AdminDashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: 1,
    },
  },
});

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoles?: string[] }> = ({
  children,
  allowedRoles,
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface">
        <div className="w-10 h-10 border-4 border-crimson border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    const roleRoutes: Record<string, string> = {
      admin: '/dashboard/admin',
      donor: '/dashboard/donor',
      blood_bank: '/dashboard/blood-bank',
      hospital: '/dashboard/blood-bank',
      patient: '/dashboard/patient',
    };
    return <Navigate to={roleRoutes[user.role] || '/dashboard/patient'} replace />;
  }

  return <>{children}</>;
};

const DashboardIndexRedirect: React.FC = () => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  const roleRoutes: Record<string, string> = {
    admin: '/dashboard/admin',
    donor: '/dashboard/donor',
    blood_bank: '/dashboard/blood-bank',
    hospital: '/dashboard/blood-bank',
    patient: '/dashboard/patient',
  };
  return <Navigate to={roleRoutes[user.role] || '/dashboard/patient'} replace />;
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Layout */}
            <Route element={<MainLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/how-it-works" element={<HowItWorksPage />} />
              <Route path="/find-blood" element={<FindBloodPage />} />
              <Route path="/become-donor" element={<BecomeDonorPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            {/* Dashboard Layout */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route
                path="patient"
                element={
                  <ProtectedRoute allowedRoles={['patient', 'admin']}>
                    <PatientDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="donor"
                element={
                  <ProtectedRoute allowedRoles={['donor', 'admin']}>
                    <DonorDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="blood-bank"
                element={
                  <ProtectedRoute allowedRoles={['blood_bank', 'hospital', 'admin']}>
                    <BloodBankDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="admin"
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
              <Route index element={<DashboardIndexRedirect />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
