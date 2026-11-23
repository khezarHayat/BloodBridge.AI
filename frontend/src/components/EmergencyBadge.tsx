import React from 'react';
import { EmergencyLevel } from '../types';

interface EmergencyBadgeProps {
  level: EmergencyLevel | string;
  size?: 'sm' | 'md';
}

export const EmergencyBadge: React.FC<EmergencyBadgeProps> = ({ level, size = 'md' }) => {
  const isCritical = level === 'critical';
  const isUrgent = level === 'urgent';

  const styles = isCritical
    ? 'bg-red-600 text-white animate-pulse'
    : isUrgent
    ? 'bg-amber-100 text-amber-800 border border-amber-300'
    : 'bg-emerald-50 text-emerald-700 border border-emerald-200';

  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold uppercase tracking-wider ${styles} ${sizeClasses}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          isCritical ? 'bg-white' : isUrgent ? 'bg-amber-600' : 'bg-emerald-500'
        }`}
      />
      {level}
    </span>
  );
};
