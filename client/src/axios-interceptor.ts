import axios from "axios";
import { useAuthStore } from "./stores/auth";
import router from "@/router"; 
import type {
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosRequestHeaders,
} from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});


// token to requests except for login and register
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("token");
    const isAuthEndpoint =
      config.url?.includes("/jwt/create") ||
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
  (response: AxiosResponse): AxiosResponse => response,
  async (error: AxiosError) => {
    const authStore = useAuthStore();

    if (error.response?.status === 401) {
        authStore.logout();
        router.push("/sign-in"); 
    }

    return Promise.reject(error); 
  }
);
export default apiClient;
