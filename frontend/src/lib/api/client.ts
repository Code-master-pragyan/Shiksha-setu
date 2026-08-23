export interface ApiErrorResponse {
  detail?: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
  error?: {
    code?: string;
    message?: string;
  };
}

export class ApiError extends Error {
  public status: number;
  public code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

import { useAuthStore } from "../store/auth";

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const token = useAuthStore.getState().token;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = "An unknown API error occurred.";
    let errorCode: string | undefined;

    try {
      const errorData = (await response.json()) as ApiErrorResponse;
      if (errorData.detail) {
        if (typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle FastAPI validation errors safely without stack traces
          errorMessage = errorData.detail
            .map((err) => `${err.loc.join(".")}: ${err.msg}`)
            .join(", ");
        }
      } else if (errorData.error) {
        errorMessage = errorData.error.message || errorMessage;
        errorCode = errorData.error.code;
      }
    } catch {
      // Non-JSON response (e.g. 500 HTML page)
      errorMessage = response.statusText || errorMessage;
    }

    throw new ApiError(response.status, errorMessage, errorCode);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return (await response.json()) as T;
}
