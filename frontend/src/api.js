import axios from 'axios';

const isDevelopment = process.env.NODE_ENV === 'development'
const baseUrl = isDevelopment ? process.env.REACT_APP_BASE_URL_LOCAL : process.env.REACT_APP_BASE_URL_PROD

const api = axios.create({
  baseURL: baseUrl,
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
