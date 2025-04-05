// Типы данных для работы с API авторизации
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  company_name?: string;
  inn?: string;
  organization_type?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
  email: string;
}

// Базовый URL API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Сервис для работы с API авторизации
const authService = {
  /**
   * Авторизует пользователя
   * @param credentials - Данные для авторизации
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка авторизации');
      }

      const data = await response.json();
      
      // Сохраняем токен и данные пользователя в localStorage
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('username', data.username);
      
      return data;
    } catch (error) {
      console.error('Error during login:', error);
      throw error;
    }
  },

  /**
   * Регистрирует нового пользователя
   * @param userData - Данные нового пользователя
   */
  async register(userData: RegisterRequest): Promise<any> {
    try {
      const response = await fetch(`${API_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка регистрации');
      }

      return await response.json();
    } catch (error) {
      console.error('Error during registration:', error);
      throw error;
    }
  },

  /**
   * Выход пользователя из системы
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
  },

  /**
   * Проверяет, авторизован ли пользователь
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },

  /**
   * Получает текущего пользователя
   */
  getCurrentUser(): { id: string; username: string } | null {
    const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');

    if (userId && username) {
      return { id: userId, username };
    }

    return null;
  },

  /**
   * Получает токен авторизации
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }
};

export default authService; 