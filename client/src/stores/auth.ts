import { defineStore } from 'pinia';
import type { AuthState, LoginCredentials, RegisterData, User, AuthResponse, ActivationResponse } from '@/types/auth';
import apiClient, { activationUrl, loginUrl, registerUrl } from '@/api/axios';

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated(): boolean {
      return !!this.token;
    },
    userFullName(): string | null {
      return this.user ? `${this.user.username}` : null;
    },
    authToken(): string | null {
      return this.token;
    },
    authError(): string | null {
      return this.error;
    },
  },

  actions: {
    setLoading(status: boolean): void {
      this.isLoading = status;
    },
    setError(error: string | null): void {
      this.error = error;
    },
    setUser(user: User | null): void {
      this.user = user;
    },
    setToken(token: string | null): void {
      this.token = token;
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },

    async login(credentials: LoginCredentials): Promise<AuthResponse | void> {
      this.setLoading(true);
      this.setError(null);          

      try {
        const { data } = await apiClient.post<AuthResponse>(loginUrl, credentials);
        this.setToken(data.access);
        // await this.refreshUserProfile();

        if (credentials.rememberMe) {
          localStorage.setItem('rememberMe', 'true');
        }
        return data;
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || 'Login failed';
        this.setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        this.setLoading(false);
      }
    },

    async register(registerData: RegisterData): Promise<void> {
      this.setLoading(true);
      this.setError(null);
      try {
        const data  = await apiClient.post<User>(registerUrl, registerData);
        console.log(data)
        // this.setUser(data)
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
        this.setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        this.setLoading(false);
      }
    },

    async activateAccount(uid:string | string[], token: string | string[]): Promise<void> {
        this.setLoading(true);
        this.setError(null);
        
        try {
          const response = await apiClient.post<ActivationResponse>(activationUrl, { uid, token });
          if (response.status === 204) {
            console.log("Ok")
          } else {
            throw new Error(response.data.message);
          }
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Account activation failed';
          this.setError(errorMessage);
          throw new Error(errorMessage);
        } finally {
          this.setLoading(false);
        }
    },

    async logout(): Promise<void> {

        this.setToken(null);
        this.setUser(null);
        localStorage.removeItem('rememberMe');
    },

    async refreshUserProfile(): Promise<void> {
      this.setLoading(true);
      try {
        const { data } = await apiClient.get<User>('/api/auth/profile');
        this.setUser(data);
      } catch (error: any) {
        if (error.response?.status === 401) await this.logout();
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    async initialize(): Promise<void> {
      const token = localStorage.getItem('token');
      if (token) {
        this.setToken(token);
        await this.refreshUserProfile();
      }
    },
  },
});
