import React from 'react';
import { Link } from 'react-router-dom';
import { HeartHandshake, Phone, MapPin, Mail, ShieldAlert } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-navy text-slate-300 pt-16 pb-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-crimson flex items-center justify-center text-white">
                <HeartHandshake className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">BloodBridge</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Every Second Matters. Every Donation Saves Lives. An intelligent emergency blood coordination network serving Peshawar, Khyber Pakhtunkhwa.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-400 pt-2">
              <MapPin className="w-4 h-4 text-crimson" />
              <span>Peshawar, Khyber Pakhtunkhwa, Pakistan</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold text-sm uppercase tracking-wider mb-4">
              Quick Links
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link to="/find-blood" className="hover:text-white transition-colors">
                  Find Blood (Emergency)
                </Link>
              </li>
              <li>
                <Link to="/become-donor" className="hover:text-white transition-colors">
                  Register as Donor
                </Link>
              </li>
              <li>
                <Link to="/how-it-works" className="hover:text-white transition-colors">
                  How BloodBridge Works
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-white transition-colors">
                  About the Platform
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-white transition-colors">
                  Contact Coordination Team
                </Link>
              </li>
            </ul>
          </div>

          {/* Partner Facilities in Peshawar */}
          <div>
            <h4 className="text-white font-semibold text-sm uppercase tracking-wider mb-4">
              Partner Hospitals
            </h4>
            <ul className="space-y-2.5 text-sm text-slate-400">
              <li>Hayatabad Medical Complex (HMC)</li>
              <li>Lady Reading Hospital (LRH)</li>
              <li>Khyber Teaching Hospital (KTH)</li>
              <li>North West General Hospital</li>
              <li>Rehman Medical Institute (RMI)</li>
            </ul>
          </div>

          {/* Emergency & Support */}
          <div>
            <h4 className="text-white font-semibold text-sm uppercase tracking-wider mb-4">
              Emergency Hotlines
            </h4>
            <div className="space-y-3 text-sm">
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="text-xs text-slate-400 font-medium">Rescue 1122 KP</p>
                <p className="text-lg font-bold text-white tracking-wider">1122</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="text-xs text-slate-400 font-medium">Coordination Support</p>
                <p className="text-sm font-semibold text-white">+92 (091) 584-0000</p>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer Banner */}
        <div className="mt-12 pt-8 border-t border-slate-800">
          <div className="flex items-start gap-3 p-4 rounded-xl bg-charcoal/80 border border-slate-700/60 text-xs text-slate-400">
            <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <p>
              <strong className="text-slate-200">Medical Notice:</strong> BloodBridge facilitates intelligent discovery and coordination between donors and recipients. Automated matching does not guarantee medical transfusion compatibility. All blood products and donors must be screened and cross-matched by qualified laboratory staff before transfusion.
            </p>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
            <p>© {new Date().getFullYear()} BloodBridge Technologies. All rights reserved. Peshawar Prototype.</p>
            <div className="flex gap-6">
              <Link to="/about" className="hover:text-slate-400">Privacy Policy</Link>
              <Link to="/about" className="hover:text-slate-400">Terms of Service</Link>
              <Link to="/contact" className="hover:text-slate-400">Support</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
