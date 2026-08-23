// EXACT matches of Backend Pydantic Schemas

// ----------------------------------------------------
// Auth Schemas
// ----------------------------------------------------

export interface LoginRequest {
  email: string;
  password: string;
  role: string;
}

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
  student_id?: string;
}

export interface Citation {
  source_title: string;
  chapter: string;
  section?: string | null;
  page_start: number;
  page_end: number;
  citation_text: string;
}

// ----------------------------------------------------
// Doubt Schemas
// ----------------------------------------------------

export interface DoubtRequest {
  student_id?: string | null;
  question: string;
  grade: number;
  subject: string;
  preferred_language: string;
  top_k: number;
}

export interface DoubtResponse {
  question: string;
  answer: string;
  key_points: string[];
  learning_level?: string | null;
  confidence: "high" | "medium" | "low";
  citations: Citation[];
  follow_up_question?: string | null;
  concept_id?: string | null;
}

// ----------------------------------------------------
// Practice Schemas
// ----------------------------------------------------

export interface PracticeGenerateRequest {
  student_id: string;
  concept_id: string;
  subject: string;
}

export interface PracticeGenerateResponse {
  question_id: string;
  question_text: string;
  question_type: string;
  options?: string[] | null;
  difficulty: string;
  concept_id: string;
  citations: Citation[];
}

export interface PracticeAttemptRequest {
  student_id: string;
  question_id: string;
  student_answer: string;
  time_taken?: number | null;
  hint_used: boolean;
}

export interface PracticeAttemptResponse {
  correct: boolean;
  feedback: string;
  mastery_score: number;
  learning_level: string;
  consecutive_errors: number;
  next_action: string;
  next_difficulty: string;
  citations: Citation[];
}

// ----------------------------------------------------
// Retrieval Schemas
// ----------------------------------------------------

export interface RetrievalRequest {
  query: string;
  grade?: number | null;
  subject?: string | null;
  language?: string | null;
  chapter?: string | null;
  top_k: number;
}

export interface RetrievalResult {
  chunk_id: string;
  text: string;
  title: string;
  chapter_number?: number | null;
  chapter?: string | null;
  section?: string | null;
  page_start: number;
  page_end: number;
  subject: string;
  grade: number;
  language: string;
  similarity_score: number;
}

export interface RetrievalResponse {
  query: string;
  results: RetrievalResult[];
}

// ----------------------------------------------------
// Teacher Schemas
// ----------------------------------------------------

export interface TeacherInsight {
  student_id: string;
  concept_id: string;
  concept_name: string;
  mastery_score: number;
  recent_accuracy?: number | null;
  consecutive_errors: number;
  status: string;
  trend: string;
  reason: string;
  recommended_action: string;
}

export interface TeacherSummaryResponse {
  total_students: number;
  at_risk: number;
  needs_attention: number;
  improving: number;
  on_track: number;
  insights: TeacherInsight[];
}

export interface StudentDetailResponse {
  student_id: string;
  grade: number;
  preferred_language: string;
  insights: TeacherInsight[];
}

// ----------------------------------------------------
// Frontend-Only Types 
// (Currently none; all above map directly to backend)
// ----------------------------------------------------

export interface StudentInfo {
  id: string;
  name: string;
  grade: number;
  preferred_language: string;
}

export interface ConceptMasteryItem {
  concept_id: string;
  concept_name: string;
  score: number;
  attempts: number;
  last_attempt: string | null;
}

export interface StudentDashboardResponse {
  student: StudentInfo;
  overall_mastery: number;
  accuracy_rate: number;
  concepts: ConceptMasteryItem[];
}

export interface StudentProfileResponse {
  id: string;
  user_id: string;
  name: string;
  email: string;
  grade: number;
  preferred_language: string;
}

export interface StudentProfileUpdate {
  preferred_language?: string;
}

// Teacher Insights
