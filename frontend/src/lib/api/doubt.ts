import { apiClient } from "./client";
import { DoubtRequest, DoubtResponse } from "@/types/api";

/**
 * Frontend function: askDoubt
 * HTTP method: POST
 * Backend URL: /api/v1/doubt/ask
 * Request type: DoubtRequest
 * Response type: DoubtResponse
 */
export async function askDoubt(request: DoubtRequest): Promise<DoubtResponse> {
  return apiClient<DoubtResponse>("/api/v1/doubt/ask", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
