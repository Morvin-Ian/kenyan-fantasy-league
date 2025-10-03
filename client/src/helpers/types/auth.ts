export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone_number: string | null;
  profile_photo: string;
  gender: string;
  country: string;
  city: string;
  is_admin: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  first_name: string | null;
  last_name: string | null;
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

export interface PasswordResetData {
  new_password: string;
  re_new_password: string;
  uid: string;
  token: string;
}


