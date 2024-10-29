import { defineStore } from 'pinia';
import type { AuthState, LoginCredentials, RegisterData, User, AuthResponse, ActivationResponse } from '@/types/auth';
import apiClient from '@/api/axios';

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated(): boolean {
      return !!this.token && !!this.user;
    },
    userFullName(): string | null {
      return this.user ? `${this.user.username}` : null;
    },
    isEmailVerified(): boolean {
      return !!this.user?.isEmailVerified;
    },
    isAdmin(): boolean {
      return this.user?.role === 'admin';
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
        const { data } = await apiClient.post<AuthResponse>('/auth/jwt/create/', credentials);
        this.setToken(data.access);
        await this.refreshUserProfile();

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

    async register(registerData: RegisterData): Promise<string | void> {
      this.setLoading(true);
      this.setError(null);
      try {
        const { data } = await apiClient.post<{ activationUrl: string }>('/auth/users/', registerData);
        return data.activationUrl;
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || 'Registration failed';
        this.setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        this.setLoading(false);
      }
    },

    async activateAccount(activationToken: string): Promise<void> {
      this.setLoading(true);
      this.setError(null);
      try {
        const { data } = await apiClient.post<ActivationResponse>('/auth/users/activation', { token: activationToken });
        if (!data.success) throw new Error(data.message);
      } catch (error: any) {
        const errorMessage = error.response?.data?.message || 'Account activation failed';
        this.setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        this.setLoading(false);
      }
    },

    async logout(): Promise<void> {
      try {
        if (this.token) await apiClient.post('/api/auth/logout');
      } finally {
        this.setToken(null);
        this.setUser(null);
        localStorage.removeItem('rememberMe');
      }
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
