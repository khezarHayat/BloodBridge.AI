import React from 'react';
import {
  GitCommit,
  CheckCircle2,
  Clock,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Cpu,
  MapPin,
} from 'lucide-react';
import { BloodGroupBadge } from '../components/BloodGroupBadge';

export const HowItWorksPage: React.FC = () => {
  const compatibilityTable = [
    { recipient: 'O-', canReceive: ['O-'], canDonateTo: ['All Blood Groups (Universal Donor)'] },
    { recipient: 'O+', canReceive: ['O+', 'O-'], canDonateTo: ['O+', 'A+', 'B+', 'AB+'] },
    { recipient: 'A-', canReceive: ['A-', 'O-'], canDonateTo: ['A-', 'A+', 'AB-', 'AB+'] },
    { recipient: 'A+', canReceive: ['A+', 'A-', 'O+', 'O-'], canDonateTo: ['A+', 'AB+'] },
    { recipient: 'B-', canReceive: ['B-', 'O-'], canDonateTo: ['B-', 'B+', 'AB-', 'AB+'] },
    { recipient: 'B+', canReceive: ['B+', 'B-', 'O+', 'O-'], canDonateTo: ['B+', 'AB+'] },
    { recipient: 'AB-', canReceive: ['AB-', 'A-', 'B-', 'O-'], canDonateTo: ['AB-', 'AB+'] },
    { recipient: 'AB+', canReceive: ['All Blood Groups (Universal Recipient)'], canDonateTo: ['AB+'] },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 space-y-16">
      {/* Header */}
      <div className="max-w-3xl mx-auto text-center space-y-3">
        <span className="text-xs uppercase font-bold text-crimson tracking-wider">
          Architecture & Workflow
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-navy">
          How BloodBridge Coordinates Emergency Blood
        </h1>
        <p className="text-slate-600 text-sm sm:text-base">
          From hospital ward request to verified donor arrival in Peshawar in four structured steps.
        </p>
      </div>

      {/* The 4 Steps */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-3">
          <div className="w-10 h-10 rounded-xl bg-crimson text-white flex items-center justify-center font-bold">
            1
          </div>
          <h3 className="font-bold text-navy text-base">Request Initiated</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Patient attendants specify blood group, units, hospital (e.g., KTH, HMC, or LRH), and emergency status.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-3">
          <div className="w-10 h-10 rounded-xl bg-navy text-white flex items-center justify-center font-bold">
            2
          </div>
          <h3 className="font-bold text-navy text-base">Python Matching Engine</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Haversine spatial calculations find donors within 10 km, ranking by availability and recency.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold">
            3
          </div>
          <h3 className="font-bold text-navy text-base">Private Dispatch</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Eligible donors receive immediate notifications and can accept or decline without public exposure.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-3">
          <div className="w-10 h-10 rounded-xl bg-charcoal text-white flex items-center justify-center font-bold">
            4
          </div>
          <h3 className="font-bold text-navy text-base">Hospital Cross-Match</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            The donor arrives at the designated Peshawar blood bank for clinical testing and safe transfusion.
          </p>
        </div>
      </div>

      {/* Compatibility Matrix Table */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-subtle space-y-6">
        <div>
          <h2 className="text-xl font-bold text-navy">
            Clinical Blood Group Compatibility Matrix
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Red blood cell compatibility reference used by BloodBridge algorithms.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-surface">
                <th className="py-3 px-4 font-bold text-navy">Recipient Blood Type</th>
                <th className="py-3 px-4 font-bold text-navy">Can Safely Receive From</th>
                <th className="py-3 px-4 font-bold text-navy">Can Safely Donate To</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {compatibilityTable.map((row) => (
                <tr key={row.recipient} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-crimson">
                    <BloodGroupBadge bloodGroup={row.recipient} size="sm" />
                  </td>
                  <td className="py-3 px-4 text-slate-700 font-medium">
                    {row.canReceive.join(', ')}
                  </td>
                  <td className="py-3 px-4 text-slate-700 font-medium">
                    {row.canDonateTo.join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-subtle space-y-6">
        <h2 className="text-xl font-bold text-navy flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-crimson" />
          Frequently Asked Questions
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-600">
          <div className="space-y-1.5">
            <h4 className="font-bold text-navy text-sm">How is donor privacy protected?</h4>
            <p className="leading-relaxed">
              Donors' exact GPS coordinates and contact phone numbers are never published on the public website. Only once an invitation is accepted does the requester receive verified contact details.
            </p>
          </div>

          <div className="space-y-1.5">
            <h4 className="font-bold text-navy text-sm">Is automated matching clinically certified?</h4>
            <p className="leading-relaxed">
              Automated matching determines theoretical ABO/Rh eligibility. Actual transfusion compatibility must always be verified by hospital blood bank technicians through laboratory cross-matching.
            </p>
          </div>

          <div className="space-y-1.5">
            <h4 className="font-bold text-navy text-sm">How often can I donate blood?</h4>
            <p className="leading-relaxed">
              Healthy adults can donate whole blood every 56 days (8 weeks). Our platform automatically locks donor availability for 56 days following a confirmed donation.
            </p>
          </div>

          <div className="space-y-1.5">
            <h4 className="font-bold text-navy text-sm">Which areas in Peshawar are covered?</h4>
            <p className="leading-relaxed">
              We currently cover all major sectors including Hayatabad, University Town, Saddar, Gulbahar, Warsak Road, Ring Road, and surrounding localities.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
