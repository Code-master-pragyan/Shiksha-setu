import { apiClient } from "./client";
import {
  PracticeGenerateRequest,
  PracticeGenerateResponse,
  PracticeAttemptRequest,
  PracticeAttemptResponse,
} from "@/types/api";

/**
 * Frontend function: generatePractice
 * HTTP method: POST
 * Backend URL: /api/v1/practice/generate
 * Request type: PracticeGenerateRequest
 * Response type: PracticeGenerateResponse
 */
export async function generatePractice(
  request: PracticeGenerateRequest
): Promise<PracticeGenerateResponse> {
  return apiClient<PracticeGenerateResponse>("/api/v1/practice/generate", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * Frontend function: submitPracticeAttempt
 * HTTP method: POST
 * Backend URL: /api/v1/practice/attempt
 * Request type: PracticeAttemptRequest
 * Response type: PracticeAttemptResponse
 */
export async function submitPracticeAttempt(
  request: PracticeAttemptRequest
): Promise<PracticeAttemptResponse> {
  return apiClient<PracticeAttemptResponse>("/api/v1/practice/attempt", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
