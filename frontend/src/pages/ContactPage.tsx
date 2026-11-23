import React, { useState } from 'react';
import {
  Mail,
  Phone,
  MapPin,
  Send,
  CheckCircle,
  Building,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { api } from '../services/api';

export const ContactPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await api.sendContact({ name, email, phone, subject, message });
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Failed to submit inquiry. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 space-y-12">
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <span className="text-xs uppercase font-bold text-crimson tracking-wider">
          Get in Touch
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-navy">
          Contact BloodBridge Peshawar
        </h1>
        <p className="text-slate-600 text-sm">
          Have questions about institutional integration, volunteer donor drives, or hospital onboarding? Our coordination team is here to assist.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Contact Form */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-8 border border-slate-200 shadow-subtle">
          {submitted ? (
            <div className="text-center py-12 space-y-4">
              <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
                <CheckCircle className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-navy">Inquiry Received</h3>
              <p className="text-xs text-slate-600 max-w-md mx-auto">
                Thank you for contacting BloodBridge Peshawar. Our team will review your message and respond within 24 hours.
              </p>
              <button
                onClick={() => {
                  setSubmitted(false);
                  setName('');
                  setEmail('');
                  setPhone('');
                  setSubject('');
                  setMessage('');
                }}
                className="mt-4 px-5 py-2 rounded-lg bg-navy text-white text-xs font-semibold hover:bg-navy-600 transition-colors"
              >
                Send Another Message
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 rounded-lg bg-red-50 text-red-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Your Full Name</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Dr. Salman Afridi"
                    className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Contact Phone</label>
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

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="salman@hospital.org"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Subject</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Hospital Inventory Integration / Donor Drive"
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Message</label>
                <textarea
                  required
                  rows={4}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Provide details about your facility, inquiry, or partnership request..."
                  className="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-crimson focus:ring-crimson"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 px-4 rounded-xl bg-crimson hover:bg-crimson-600 text-white font-bold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  'Transmitting Inquiry...'
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Submit Inquiry
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Emergency Contacts & Info */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-navy rounded-2xl p-6 text-white space-y-4">
            <h3 className="font-bold text-base flex items-center gap-2">
              <Phone className="w-5 h-5 text-crimson-400" />
              Emergency Hotlines (Peshawar)
            </h3>
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-white/5 rounded-xl border border-white/10 flex justify-between items-center">
                <div>
                  <p className="font-semibold text-white">Rescue 1122 KPK</p>
                  <p className="text-slate-400">Ambulance & Trauma Response</p>
                </div>
                <span className="text-lg font-bold text-crimson-300">1122</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/10 flex justify-between items-center">
                <div>
                  <p className="font-semibold text-white">Lady Reading Hospital</p>
                  <p className="text-slate-400">Emergency & Blood Bank</p>
                </div>
                <span className="text-sm font-semibold text-slate-200">(091) 9211430</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/10 flex justify-between items-center">
                <div>
                  <p className="font-semibold text-white">Hayatabad Medical Complex</p>
                  <p className="text-slate-400">Trauma Unit</p>
                </div>
                <span className="text-sm font-semibold text-slate-200">(091) 9217140</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-subtle space-y-3 text-xs text-slate-600">
            <h4 className="font-bold text-navy text-sm flex items-center gap-2">
              <MapPin className="w-4 h-4 text-crimson" />
              Coordination Center
            </h4>
            <p>Phase 3, Hayatabad, Peshawar, Khyber Pakhtunkhwa, 25000</p>
            <p className="text-slate-500 flex items-center gap-1.5 pt-1">
              <Clock className="w-3.5 h-3.5" />
              24/7 Automated Emergency Dispatch
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
