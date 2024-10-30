import axios from 'axios';
import type { AxiosResponse, AxiosError, InternalAxiosRequestConfig, AxiosRequestHeaders } from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
});

export const loginUrl = `/auth/jwt/create/`
export const registerUrl = `/auth/users/`
export const activationUrl = `/auth/users/activation/`

// Add token to requests except for login and register
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    const isAuthEndpoint = config.url?.includes('/jwt/create') || config.url?.includes('/auth/users/');

    if (token && !isAuthEndpoint) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`
      } as AxiosRequestHeaders;  
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Handle token expiration and other response errors
// apiClient.interceptors.response.use(
//   (response: AxiosResponse): AxiosResponse => response,
//   async (error: AxiosError) => {
//     if (error.response?.status === 401) {
//       localStorage.removeItem('token');
//       window.location.href = '/sign-in';
//     }
//     return Promise.reject(error);
//   }
// );

export default apiClient;
