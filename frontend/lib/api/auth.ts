import { apiFetch } from "./client";

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: "ADMIN" | "DOCTOR" | "NURSE";
  is_active: boolean;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

const ACCESS_TOKEN_KEY = "medivoice_access_token";
const REFRESH_TOKEN_KEY = "medivoice_refresh_token";
const USER_KEY = "medivoice_user";

export function setTokens(data: LoginResponse) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  return raw ? (JSON.parse(raw) as AuthUser) : null;
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

/** POST /auth/login */
export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const data = await apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
    skipAuth: true,
  });
  setTokens(data);
  return data;
}

/**
 * POST /auth/refresh
 * Exported separately so client.ts can call it directly on a 401
 * without creating a circular import through apiFetch.
 */
export async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const data = await apiFetch<LoginResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
      skipAuth: true,
      skip401Handling: true,
    });
    setTokens(data);
    return data.access_token;
  } catch {
    return null;
  }
}

/** POST /auth/logout, then clear local state regardless of outcome */
export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken();
  try {
    if (refreshToken) {
      await apiFetch("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
        skip401Handling: true,
      });
    }
  } catch {
    // Backend logout failing shouldn't block clearing local state.
  } finally {
    clearTokens();
  }
}

/** GET /auth/me */
export async function getCurrentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/auth/me");
}
