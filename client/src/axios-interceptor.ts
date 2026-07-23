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

    const isRefreshRequest = originalRequest?.url?.includes("/jwt/refresh");
    const isAuthEndpoint = originalRequest?.url?.includes("/jwt/create") ||
      originalRequest?.url?.includes("/auth/users/");

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      // If the refresh token request itself failed, logout only on auth errors
      if (isRefreshRequest) {
        isRefreshing = false;
        subscribers = []; // Clear any pending requests
        authStore.setLoading(false); // Ensure loading state is cleared
        // Only logout if the error is auth-related (401/403), not a network error
        const refreshStatus = error.response?.status;
        if (refreshStatus === 401 || refreshStatus === 403) {
          await authStore.logout();
          router.push("/sign-in");
        }
        return Promise.reject(error);
      }

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
          subscribers = [];
          authStore.setLoading(false);
          // Only logout on auth errors, not transient network/server errors
          const axiosErr = e as AxiosError;
          const errStatus = axiosErr?.response?.status;
          if (errStatus === 401 || errStatus === 403) {
            await authStore.logout();
            router.push("/sign-in");
          }
          return Promise.reject(e);
        }
      }

      return new Promise((resolve, reject) => {
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