import axios from 'axios';

const isDevelopment = import.meta.env.MODE === 'development'

const api = axios.create({
  baseURL: isDevelopment ? import.meta.env.REACT_API_BASE_URL_LOCAL : import.meta.env.REACT_API_BASE_URL_PROD,
});

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

export default api;
