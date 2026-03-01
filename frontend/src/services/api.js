import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

export const queryService = {
    analyze: (data) => api.post('/queries/analyze', data),
    getHistory: () => api.get('/queries/'),
    getById: (id) => api.get(`/queries/${id}`),
};

export const reportService = {
    generate: (data) => api.post('/reports/generate', data),
    render: (id) => api.get(`/reports/${id}/render`),
};

export const alertService = {
    list: () => api.get('/alerts/'),
    create: (data) => api.post('/alerts/', data),
    update: (id, data) => api.put(`/alerts/${id}`, data),
    delete: (id) => api.delete(`/alerts/${id}`),
};

export const dataSourceService = {
    list: () => api.get('/data_sources/'),
    create: (data) => api.post('/data_sources/', data),
    delete: (id) => api.delete(`/data_sources/${id}`),
};

export const authService = {
    login: (credentials) => api.post('/auth/login', credentials),
    getCurrentUser: () => api.get('/users/me'),
};

export default api;
