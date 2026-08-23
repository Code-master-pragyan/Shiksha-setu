import { apiClient } from "./client";
import type { LoginRequest, LoginResponse } from "@/types/api";

export async function login(request: LoginRequest): Promise<LoginResponse> {
  return apiClient<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
