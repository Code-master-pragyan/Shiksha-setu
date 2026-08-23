import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { LoginResponse } from "@/types/api";

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  token: string | null;
  user: UserInfo | null;
  studentId: string | null;
  setAuth: (data: LoginResponse) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

// NOTE FOR HACKATHON DEMO:
// We are using Zustand persist (localStorage) to store the JWT token instead of an HttpOnly cookie.
// This is to avoid complex CORS + Credentials setup across different localhost ports (3001 vs 8000)
// during rapid development. In production, tokens should be stored in secure HttpOnly cookies.
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      studentId: null,
      
      setAuth: (data: LoginResponse) => set({ 
        token: data.access_token, 
        user: data.user, 
        studentId: data.student_id 
      }),
      
      logout: () => set({ token: null, user: null, studentId: null }),
      
      isAuthenticated: () => !!get().token,
    }),
    {
      name: "auth-storage",
    }
  )
);
