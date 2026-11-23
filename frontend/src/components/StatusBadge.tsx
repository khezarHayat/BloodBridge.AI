import React from 'react';
import { RequestStatus } from '../types';

interface StatusBadgeProps {
  status: RequestStatus | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getBadgeStyle = (s: string) => {
    switch (s) {
      case 'fulfilled':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'matched':
      case 'donor_confirmed':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'matching':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'pending':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'cancelled':
      case 'expired':
        return 'bg-gray-100 text-gray-600 border-gray-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const formatText = (s: string) => {
    return s.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyle(
        status
      )}`}
    >
      {formatText(status)}
    </span>
  );
};
