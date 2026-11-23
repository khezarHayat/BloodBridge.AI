import React from 'react';
import { BloodGroup } from '../types';

interface BloodGroupBadgeProps {
  bloodGroup: BloodGroup | string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const BloodGroupBadge: React.FC<BloodGroupBadgeProps> = ({
  bloodGroup,
  size = 'md',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 font-bold',
    md: 'text-sm px-2.5 py-1 font-bold',
    lg: 'text-lg px-3.5 py-1.5 font-extrabold',
  };

  return (
    <span
      className={`inline-flex items-center justify-center rounded-lg bg-crimson-50 text-crimson-700 border border-crimson-200 tracking-wider font-mono shadow-sm ${sizeClasses[size]} ${className}`}
    >
      {bloodGroup}
    </span>
  );
};
