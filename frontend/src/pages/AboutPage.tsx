import React from 'react';
import {
  HeartHandshake,
  ShieldCheck,
  Zap,
  MapPin,
  Lock,
  Hospital,
  Activity,
  CheckCircle,
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
      {/* Intro */}
      <div className="max-w-3xl mx-auto text-center space-y-4">
        <span className="text-xs uppercase font-bold text-crimson tracking-wider">
          Our Startup Mission
        </span>
        <h1 className="text-4xl font-extrabold text-navy tracking-tight">
          Pioneering Emergency Blood Coordination in Peshawar
        </h1>
        <p className="text-slate-600 text-base leading-relaxed">
          BloodBridge was conceived to eliminate the desperate, chaotic search for blood donors in emergency wards across Khyber Pakhtunkhwa.
        </p>
      </div>

      {/* Grid of Values */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle space-y-4">
          <div className="w-12 h-12 rounded-xl bg-crimson-50 text-crimson flex items-center justify-center">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-navy">Rapid Matching</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            Every second counts in obstetric hemorrhages, trauma accidents on Peshawar Ring Road, and elective bypass surgeries. Our algorithms find local matches in under 30 seconds.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle space-y-4">
          <div className="w-12 h-12 rounded-xl bg-navy-50 text-navy flex items-center justify-center">
            <Lock className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-navy">Zero-Spam Privacy</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            Unlike public WhatsApp groups or social media posts, volunteer donors' personal phone numbers and identities are never exposed publicly.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle space-y-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-navy">Clinical Safety Standards</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            We partner with accredited blood banks and enforce strict medical safety parameters: minimum 56-day intervals and mandatory infection screening.
          </p>
        </div>
      </div>

      {/* Peshawar Context Section */}
      <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-card">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div className="space-y-4">
            <span className="text-xs uppercase font-bold text-crimson tracking-wider">
              Regional Scope
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-navy">
              Serving Peshawar's Leading Tertiary Healthcare Institutions
            </h2>
            <p className="text-sm text-slate-600 leading-relaxed">
              Peshawar is the medical referral capital of Khyber Pakhtunkhwa, handling patient referrals from all over Malakand, Hazara, and the Southern Districts.
            </p>
            <ul className="space-y-2.5 text-xs text-slate-700">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-crimson flex-shrink-0" />
                Lady Reading Hospital (LRH) — Peshawar City
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-crimson flex-shrink-0" />
                Hayatabad Medical Complex (HMC) — Phase 4 Hayatabad
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-crimson flex-shrink-0" />
                Khyber Teaching Hospital (KTH) — University Town
              </li>
            </ul>
          </div>

          <div className="bg-surface rounded-2xl p-6 border border-slate-200 space-y-4">
            <h4 className="font-bold text-navy text-sm">Targeted Expansion</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              While our initial focus is tightly concentrated on the Peshawar metropolitan core (Hayatabad, University Town, Saddar, Gulbahar), our roadmap includes expanding to Mardan, Abbottabad, Swat, and Kohat.
            </p>
            <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs font-mono text-slate-500">
              Coverage: Peshawar District • KPK • Pakistan
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
