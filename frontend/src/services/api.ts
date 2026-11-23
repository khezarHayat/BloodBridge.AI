const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('bloodbridge_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    let errorMsg = `Request failed: ${res.statusText}`;
    try {
      const errData = await res.json();
      errorMsg = errData.message || errData.detail || errorMsg;
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  // Public
  getPublicStats: () => request<any>('/api/public/stats'),
  getBloodGroups: () => request<any>('/api/public/blood-groups'),
  getAreas: () => request<any[]>('/api/public/areas'),
  sendContact: (data: any) => request<any>('/api/public/contact', { method: 'POST', body: JSON.stringify(data) }),

  // Auth
  register: (data: any) => request<any>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: any) => request<any>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => request<any>('/api/auth/me'),
  updateMe: (data: any) => request<any>('/api/auth/me', { method: 'PUT', body: JSON.stringify(data) }),

  // Donors
  getDonors: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/donors/${qs}`);
  },
  getMyDonorProfile: () => request<any>('/api/donors/me/profile'),
  updateDonorProfile: (donorId: string, data: any) =>
    request<any>(`/api/donors/${donorId}`, { method: 'PUT', body: JSON.stringify(data) }),
  toggleAvailability: (donorId: string, is_available: boolean) =>
    request<any>(`/api/donors/${donorId}/availability`, {
      method: 'PATCH',
      body: JSON.stringify({ is_available }),
    }),
  getMyInvitations: () => request<any>('/api/donors/me/invitations'),
  respondToInvitation: (invitationId: string, action: { status: 'accepted' | 'declined'; response_notes?: string }) =>
    request<any>(`/api/donors/invitations/${invitationId}`, { method: 'PUT', body: JSON.stringify(action) }),

  // Blood Requests
  createBloodRequest: (data: any) =>
    request<any>('/api/blood-requests/', { method: 'POST', body: JSON.stringify(data) }),
  getBloodRequests: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/blood-requests/${qs}`);
  },
  getMyRequests: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/blood-requests/my-requests${qs}`);
  },
  getBloodRequest: (id: string) => request<any>(`/api/blood-requests/${id}`),
  updateBloodRequest: (id: string, data: any) =>
    request<any>(`/api/blood-requests/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  cancelBloodRequest: (id: string, reason?: string) => {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return request<any>(`/api/blood-requests/${id}/cancel${qs}`, { method: 'PUT' });
  },
  getInvitationsForRequest: (id: string) => request<any[]>(`/api/blood-requests/${id}/invitations`),

  // Blood Banks & Inventory
  getBloodBanks: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/blood-banks/${qs}`);
  },
  getMyBloodBank: () => request<any>('/api/blood-banks/me'),
  getBankInventory: (bankId: string, params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/blood-banks/${bankId}/inventory${qs}`);
  },
  addInventoryBatch: (bankId: string, data: any) =>
    request<any>(`/api/blood-banks/${bankId}/inventory`, { method: 'POST', body: JSON.stringify(data) }),
  updateInventoryBatch: (bankId: string, batchId: string, data: any) =>
    request<any>(`/api/blood-banks/${bankId}/inventory/${batchId}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteInventoryBatch: (bankId: string, batchId: string) =>
    request<any>(`/api/blood-banks/${bankId}/inventory/${batchId}`, { method: 'DELETE' }),
  getInventorySummary: (bankId: string) => request<any[]>(`/api/blood-banks/${bankId}/inventory/summary`),

  // Notifications
  getNotifications: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/notifications/${qs}`);
  },
  getUnreadCount: () => request<any>('/api/notifications/unread-count'),
  markNotificationRead: (id: string) => request<any>(`/api/notifications/${id}/read`, { method: 'PUT' }),
  markAllNotificationsRead: () => request<any>('/api/notifications/read-all', { method: 'PUT' }),

  // Admin
  getAdminStats: () => request<any>('/api/admin/stats'),
  getAdminUsers: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/admin/users${qs}`);
  },
  verifyUser: (userId: string) => request<any>(`/api/admin/users/${userId}/verify`, { method: 'PUT' }),
  deactivateUser: (userId: string) => request<any>(`/api/admin/users/${userId}/deactivate`, { method: 'PUT' }),
  verifyBloodBank: (bankId: string) => request<any>(`/api/admin/blood-banks/${bankId}/verify`, { method: 'PUT' }),
  getAuditLogs: (params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/api/admin/audit-logs${qs}`);
  },
  getAnalyticsByGroup: () => request<any[]>('/api/admin/analytics/requests-by-group'),
  getAnalyticsByArea: () => request<any[]>('/api/admin/analytics/requests-by-area'),
  getAnalyticsInventory: () => request<any[]>('/api/admin/analytics/inventory-overview'),
};
