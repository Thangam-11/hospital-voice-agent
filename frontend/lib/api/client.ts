const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("medivoice_access_token");
}

interface ApiFetchOptions extends RequestInit {
  /** Skip attaching the Authorization header (e.g. for /auth/login) */
  skipAuth?: boolean;
  /** Skip the 401 -> refresh -> retry -> redirect flow entirely
   *  (used by refreshAccessToken/logout themselves to avoid loops) */
  skip401Handling?: boolean;
}

async function rawFetch(path: string, options?: ApiFetchOptions) {
  const token = options?.skipAuth ? null : getStoredAccessToken();

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options?.headers ?? {}),
    },
  });
}

async function parseError(response: Response): Promise<string> {
  let message = `API request failed: ${response.status}`;
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") message = body.detail;
  } catch {
    // keep default message
  }
  return message;
}

export async function apiFetch<T>(
  path: string,
  options?: ApiFetchOptions,
): Promise<T> {
  let response = await rawFetch(path, options);

  if (response.status === 401 && !options?.skip401Handling) {
    // Lazy import avoids a circular dependency between client.ts and auth.ts
    const { refreshAccessToken } = await import("./auth");
    const newToken = await refreshAccessToken();

    if (newToken) {
      response = await rawFetch(path, options);
    } else {
      if (typeof window !== "undefined") {
        const { clearTokens } = await import("./auth");
        clearTokens();
        window.location.href = "/login";
      }
      throw new Error("Session expired. Please log in again.");
    }
  }

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json() as Promise<T>;
}
