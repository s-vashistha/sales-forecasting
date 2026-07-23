import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
});

export const forecastService = {
  getForecast:     (days = 30) => api.get(`/forecast?days=${days}`),
  getHistory:      (days = 90) => api.get(`/history?days=${days}`),
  getInventory:    ()          => api.get('/inventory-recommendations'),
  getModelMetrics: ()          => api.get('/model-metrics'),
};

export default api;
