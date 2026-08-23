import { apiClient } from "./client";
import { StudentDashboardResponse, StudentProfileResponse, StudentProfileUpdate } from "@/types/api";

export async function getStudentDashboard(
  studentId: string
): Promise<StudentDashboardResponse> {
  return apiClient<StudentDashboardResponse>(
    `/api/v1/students/${studentId}/dashboard`,
    {
      method: "GET",
    }
  );
}

export async function getStudentProfile(
  studentId: string
): Promise<StudentProfileResponse> {
  return apiClient<StudentProfileResponse>(
    `/api/v1/students/${studentId}/profile`,
    {
      method: "GET",
    }
  );
}

export async function updateStudentProfile(
  studentId: string,
  update: StudentProfileUpdate
): Promise<StudentProfileResponse> {
  return apiClient<StudentProfileResponse>(
    `/api/v1/students/${studentId}/profile`,
    {
      method: "PATCH",
      body: JSON.stringify(update),
    }
  );
}
