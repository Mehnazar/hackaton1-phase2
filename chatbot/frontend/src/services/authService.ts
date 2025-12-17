/**
 * Authentication Service
 * Handles all auth-related API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface UserProfile {
  softwareBackground: "beginner" | "intermediate" | "advanced";
  hardwareBackground: "low-end" | "mid-range" | "high-end";
}

export interface User {
  id: string;
  email: string;
  name: string;
  emailVerified: boolean;
  createdAt: string;
}

export interface SessionData {
  token: string;
  user: User;
  expiresAt: string;
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
  software_background: "beginner" | "intermediate" | "advanced";
  hardware_background: "low-end" | "mid-range" | "high-end";
}

export interface SigninData {
  email: string;
  password: string;
}

class AuthService {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage
    this.token = localStorage.getItem("auth_token");
  }

  private get headers() {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async signup(data: SignupData): Promise<SessionData> {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Signup failed");
    }

    const session: SessionData = await response.json();
    this.setToken(session.token);
    return session;
  }

  async signin(data: SigninData): Promise<SessionData> {
    const response = await fetch(`${API_BASE_URL}/auth/signin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Sign in failed");
    }

    const session: SessionData = await response.json();
    this.setToken(session.token);
    return session;
  }

  async signout(): Promise<void> {
    if (!this.token) return;

    await fetch(`${API_BASE_URL}/auth/signout`, {
      method: "POST",
      headers: this.headers,
    });

    this.clearToken();
  }

  async getCurrentUser(): Promise<User | null> {
    if (!this.token) return null;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: this.headers,
      });

      if (!response.ok) {
        this.clearToken();
        return null;
      }

      return await response.json();
    } catch (error) {
      this.clearToken();
      return null;
    }
  }

  async getChapterPreference(chapterId: string) {
    const response = await fetch(
      `${API_BASE_URL}/auth/chapter/${chapterId}/preference`,
      { headers: this.headers }
    );

    if (!response.ok) return null;
    return await response.json();
  }

  async updateChapterPreference(
    chapterId: string,
    updates: {
      personalized?: boolean;
      translated_to_urdu?: boolean;
      difficulty_level?: string;
    }
  ) {
    const response = await fetch(
      `${API_BASE_URL}/auth/chapter/${chapterId}/preference`,
      {
        method: "PUT",
        headers: this.headers,
        body: JSON.stringify(updates),
      }
    );

    return await response.json();
  }

  async personalizeChapter(chapterId: string, content: string, title: string) {
    const response = await fetch(
      `${API_BASE_URL}/auth/chapter/${chapterId}/personalize`,
      {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ content, title }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to personalize content");
    }

    return await response.json();
  }

  async translateChapter(chapterId: string, content: string, title: string) {
    const response = await fetch(
      `${API_BASE_URL}/auth/chapter/${chapterId}/translate`,
      {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ content, title }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to translate content");
    }

    return await response.json();
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem("auth_token");
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }
}

export const authService = new AuthService();
