import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Heart,
  Droplet,
  ShieldCheck,
  Zap,
  MapPin,
  Clock,
  ArrowRight,
  Users,
  Building2,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';
import { BloodGroupBadge } from '../components/BloodGroupBadge';
import { StatsCard } from '../components/StatsCard';
import { api } from '../services/api';
import { PublicStats } from '../types';

export const HomePage: React.FC = () => {
  const [stats, setStats] = useState<PublicStats>({
    registered_donors: 148,
    lives_impacted: 396,
    fulfilled_requests: 132,
    verified_blood_banks: 6,
    active_emergency_requests: 4,
    district: 'Peshawar',
  });

  useEffect(() => {
    api.getPublicStats()
      .then((data) => {
        if (data && data.registered_donors !== undefined) {
          setStats(data);
        }
      })
      .catch(() => {
        // Fallback demo data
      });
  }, []);

  const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  const peshawarAreas = [
    'Hayatabad',
    'University Town',
    'Saddar',
    'Gulbahar',
    'Warsak Road',
    'Ring Road',
  ];

  return (
    <div className="space-y-20 pb-20">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden bg-gradient-to-b from-navy-50/50 via-white to-surface pt-16 pb-24 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            {/* Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-crimson-50 border border-crimson-200 text-crimson-700 text-xs font-semibold uppercase tracking-wider mb-6">
              <span className="w-2 h-2 rounded-full bg-crimson animate-ping" />
              Peshawar Emergency Coordination Network
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-navy tracking-tight leading-tight">
              Every Second Matters. <br />
              <span className="text-crimson">Every Donation</span> Saves Lives.
            </h1>

            {/* Subheading */}
            <p className="mt-6 text-lg sm:text-xl text-slate-600 leading-relaxed font-normal">
              Connecting patients with potential blood donors and verified blood banks through an
              intelligent emergency blood network in Peshawar, Khyber Pakhtunkhwa.
            </p>

            {/* CTAs */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/find-blood"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-base shadow-elevated hover:shadow-lg transition-all flex items-center justify-center gap-2 group"
              >
                <Droplet className="w-5 h-5 group-hover:scale-110 transition-transform" />
                Find Blood Urgently
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/become-donor"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-navy hover:bg-navy-600 text-white font-bold text-base shadow-card transition-all flex items-center justify-center gap-2"
              >
                <Heart className="w-5 h-5 text-crimson-400" />
                Become a Donor
              </Link>
            </div>

            {/* Quick area badges */}
            <div className="mt-10 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-500">
              <span className="font-semibold text-slate-700 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-crimson" /> Active Coverage:
              </span>
              {peshawarAreas.map((area) => (
                <span key={area} className="px-2.5 py-1 rounded-md bg-white border border-slate-200">
                  {area}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* LIVE IMPACT METRICS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12 relative z-20">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Registered Donors"
            value={stats.registered_donors}
            subtitle="Verified volunteers in Peshawar"
            icon={Users}
            variant="crimson"
          />
          <StatsCard
            title="Lives Impacted"
            value={stats.lives_impacted}
            subtitle="Calculated at 3 lives per unit"
            icon={Heart}
            variant="emerald"
          />
          <StatsCard
            title="Requests Fulfilled"
            value={stats.fulfilled_requests}
            subtitle="Completed hospital transfusions"
            icon={CheckCircle2}
            variant="navy"
          />
          <StatsCard
            title="Partner Blood Banks"
            value={stats.verified_blood_banks}
            subtitle="HMC, LRH, KTH & accredited labs"
            icon={Building2}
            variant="amber"
          />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs uppercase font-bold text-crimson tracking-wider">
            Intelligent Coordination
          </span>
          <h2 className="text-3xl font-extrabold text-navy mt-2">
            How BloodBridge Works in Seconds
          </h2>
          <p className="text-slate-600 mt-3 text-sm">
            Our Python-powered matching algorithm rapidly evaluates medical compatibility, geographic distance, and donor availability across Peshawar.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle relative">
            <div className="w-12 h-12 rounded-xl bg-crimson-50 text-crimson flex items-center justify-center font-bold text-xl mb-6 border border-crimson-100">
              01
            </div>
            <h3 className="text-lg font-bold text-navy">Submit Blood Request</h3>
            <p className="text-slate-600 text-sm mt-3 leading-relaxed">
              Family members or hospital attendants input the required blood group, units, hospital (e.g., Lady Reading or HMC), and emergency urgency level.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle relative">
            <div className="w-12 h-12 rounded-xl bg-navy-50 text-navy flex items-center justify-center font-bold text-xl mb-6 border border-navy-100">
              02
            </div>
            <h3 className="text-lg font-bold text-navy">AI Matching Engine</h3>
            <p className="text-slate-600 text-sm mt-3 leading-relaxed">
              The platform executes spatial proximity scoring, compatibility rules, and verifies 56-day safe donation intervals to identify ideal local donors.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle relative">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-xl mb-6 border border-emerald-100">
              03
            </div>
            <h3 className="text-lg font-bold text-navy">Direct Coordination</h3>
            <p className="text-slate-600 text-sm mt-3 leading-relaxed">
              Matched donors receive instant alerts. Once accepted, hospital coordination takes place while strictly protecting private personal donor data.
            </p>
          </div>
        </div>
      </section>

      {/* BLOOD GROUP COMPATIBILITY OVERVIEW */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 lg:p-12 shadow-sm">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <span className="text-xs uppercase font-bold text-crimson tracking-wider">
                Clinical Overview
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-navy mt-2">
                Blood Group Compatibility Matrix
              </h2>
              <p className="text-slate-600 text-sm mt-4 leading-relaxed">
                Knowing your blood type can save minutes during critical trauma or obstetrics emergencies in Peshawar.
                <strong> O- negative</strong> is the universal red blood cell donor, whereas <strong>AB+ positive</strong> is the universal recipient.
              </p>

              <div className="mt-6 flex flex-wrap gap-2">
                {bloodGroups.map((bg) => (
                  <BloodGroupBadge key={bg} bloodGroup={bg} size="lg" />
                ))}
              </div>

              <div className="mt-8">
                <Link
                  to="/how-it-works"
                  className="text-sm font-semibold text-crimson hover:text-crimson-700 flex items-center gap-1.5"
                >
                  View complete medical compatibility chart
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            <div className="bg-surface rounded-xl p-6 border border-slate-200 space-y-4">
              <h4 className="font-bold text-navy text-sm uppercase tracking-wider">Emergency Guidelines</h4>
              <div className="space-y-3 text-xs text-slate-600">
                <div className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span>Donors must weigh at least 50 kg and be between 18 and 60 years of age.</span>
                </div>
                <div className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span>A minimum safe window of 56 days (8 weeks) between whole blood donations is strictly enforced.</span>
                </div>
                <div className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <span>Every blood unit undergoes rigorous infectious disease screening (Hepatitis B/C, HIV, Syphilis, Malaria).</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-navy rounded-3xl p-10 lg:p-16 text-center text-white relative overflow-hidden shadow-elevated">
          <div className="max-w-2xl mx-auto space-y-6 relative z-10">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Ready to Save a Life in Peshawar?
            </h2>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Join hundreds of registered volunteer blood donors across Hayatabad, University Town, Saddar, and Peshawar district. Your single donation can save up to three lives.
            </p>
            <div className="pt-4 flex flex-col sm:flex-row justify-center gap-4">
              <Link
                to="/become-donor"
                className="px-8 py-3.5 rounded-xl bg-crimson hover:bg-crimson-600 font-bold text-white shadow transition-all"
              >
                Register as Blood Donor
              </Link>
              <Link
                to="/find-blood"
                className="px-8 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 font-bold text-white border border-white/20 transition-all"
              >
                Request Emergency Blood
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
