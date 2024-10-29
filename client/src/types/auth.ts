export interface User {
    id: number;
    email: string;
    username: string;
    role: 'user' | 'admin';
    isEmailVerified: boolean;
    createdAt: string;
    lastLogin: string;
  }
  
  export interface LoginCredentials {
    email: string;
    password: string;
    rememberMe?: boolean;
  }
  
  export interface RegisterData {
    email: string;
    password: string;
    username: string;
    re_password: string;
  }
  
  export interface AuthState {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    error: string | null;
  }
  
  export interface AuthResponse {
    refresh: string;
    access: string;
  }
  
  export interface ActivationResponse {
    message: string;
    success: boolean;
  }