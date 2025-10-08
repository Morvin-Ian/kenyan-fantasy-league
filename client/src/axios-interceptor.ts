import axios from "axios";
import { useAuthStore } from "./stores/auth";
import router from "@/router"; 
import type {
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosRequestHeaders,
} from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});


let isRefreshing = false;
let subscribers: ((token: string) => void)[] = [];

function onTokenRefreshed(token: string) {
  subscribers.forEach((callback) => callback(token));
  subscribers = [];
}

function addSubscriber(callback: (token: string) => void) {
  subscribers.push(callback);
}

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("token");
    const isAuthEndpoint =
      config.url?.includes("/jwt/create") ||
      config.url?.includes("/jwt/refresh") ||
      config.url?.includes("/auth/users/");

    if (token && !isAuthEndpoint) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      } as AxiosRequestHeaders;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore();
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;

        try {
          await authStore.refreshToken(); 
          isRefreshing = false;
          const newToken = authStore.token!;
          onTokenRefreshed(newToken);
          return apiClient(originalRequest); 
        } catch (e) {
          isRefreshing = false;
          authStore.logout();
          router.push("/sign-in");
          return Promise.reject(e);
        }
      }

      return new Promise((resolve) => {
        addSubscriber((token: string) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(apiClient(originalRequest));
        });
      });
    }

    return Promise.reject(error);
  },
);

export default apiClient;