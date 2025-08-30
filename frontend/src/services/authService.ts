import { api } from './api';
import { User } from '../store/authStore';

export interface LoginRequest {
  username: string; // Email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/auth/register', userData);
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/auth/test-token');
    return response.data;
  }

  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email });
  }

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  }

  // Helper method to convert API user response to store user format
  transformUser(apiUser: UserResponse): User {
    return {
      id: apiUser.id,
      email: apiUser.email,
      firstName: apiUser.first_name,
      lastName: apiUser.last_name,
      isActive: apiUser.is_active,
      isVerified: apiUser.is_verified,
      createdAt: apiUser.created_at,
    };
  }
}

export const authService = new AuthService();
