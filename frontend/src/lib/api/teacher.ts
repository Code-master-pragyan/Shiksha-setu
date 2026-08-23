import { apiClient } from "./client";
import { TeacherSummaryResponse, StudentDetailResponse } from "@/types/api";

/**
 * Frontend function: getTeacherInsights
 * HTTP method: GET
 * Backend URL: /api/v1/teacher/insights
 * Request type: Query params (grade, subject, concept_id, status)
 * Response type: TeacherSummaryResponse
 */
export async function getTeacherInsights(params?: {
  grade?: number;
  subject?: string;
  concept_id?: string;
  status?: string;
}): Promise<TeacherSummaryResponse> {
  const urlParams = new URLSearchParams();
  if (params) {
    if (params.grade !== undefined) urlParams.append("grade", params.grade.toString());
    if (params.subject) urlParams.append("subject", params.subject);
    if (params.concept_id) urlParams.append("concept_id", params.concept_id);
    if (params.status) urlParams.append("status", params.status);
  }

  const queryString = urlParams.toString();
  const endpoint = `/api/v1/teacher/insights${queryString ? `?${queryString}` : ""}`;

  return apiClient<TeacherSummaryResponse>(endpoint, {
    method: "GET",
  });
}

/**
 * Frontend function: getStudentInsights
 * HTTP method: GET
 * Backend URL: /api/v1/teacher/students/{student_id}/insights
 * Request type: Path param (student_id)
 * Response type: StudentDetailResponse
 */
export async function getStudentInsights(
  studentId: string
): Promise<StudentDetailResponse> {
  return apiClient<StudentDetailResponse>(
    `/api/v1/teacher/students/${encodeURIComponent(studentId)}/insights`,
    {
      method: "GET",
    }
  );
}
