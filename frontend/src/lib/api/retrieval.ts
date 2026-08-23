import { apiClient } from "./client";
import { RetrievalRequest, RetrievalResponse } from "@/types/api";

/**
 * Frontend function: searchRetrieval
 * HTTP method: POST
 * Backend URL: /api/v1/retrieval/search
 * Request type: RetrievalRequest
 * Response type: RetrievalResponse
 */
export async function searchRetrieval(
  request: RetrievalRequest
): Promise<RetrievalResponse> {
  return apiClient<RetrievalResponse>("/api/v1/retrieval/search", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
