"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "motion/react";
import { useAuthStore } from "@/lib/store/auth";
import { getStudentDashboard } from "@/lib/api/student";
import { generatePractice, submitPracticeAttempt } from "@/lib/api/practice";
import type { 
  StudentDashboardResponse,
  PracticeGenerateResponse,
  PracticeAttemptResponse,
  ConceptMasteryItem
} from "@/types/api";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Brain, ChevronLeft, AlertCircle, BookOpen, Sparkles } from "lucide-react";
import { MasteryBar, McqOption } from "@/components/shared/PracticeUI";

export default function StudentPracticePage() {
  const studentId = useAuthStore(state => state.studentId);
  const [dashboardData, setDashboardData] = useState<StudentDashboardResponse | null>(null);
  const [isLoadingConcepts, setIsLoadingConcepts] = useState(true);
  const [conceptsError, setConceptsError] = useState<string | null>(null);

  const [selectedConcept, setSelectedConcept] = useState<ConceptMasteryItem | null>(null);

  // Practice State
  const [practiceQuestion, setPracticeQuestion] = useState<PracticeGenerateResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [attemptResult, setAttemptResult] = useState<PracticeAttemptResponse | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [practiceCount, setPracticeCount] = useState(0);

  // Load Concepts
  useEffect(() => {
    async function loadConcepts() {
      try {
        setIsLoadingConcepts(true);
        setConceptsError(null);
        if (!studentId) {
          throw new Error("Student ID is missing from session.");
        }
        const data = await getStudentDashboard(studentId);
        setDashboardData(data);
      } catch (err: unknown) {
        console.error("Failed to load dashboard:", err);
        const e = err as Error;
        setConceptsError(e.message || "Failed to load your concepts. Please try again later.");
      } finally {
        setIsLoadingConcepts(false);
      }
    }
    loadConcepts();
  }, [studentId]);

  // Practice Loop
  const startPractice = async (concept: ConceptMasteryItem) => {
    setSelectedConcept(concept);
    setPracticeCount(0);
    await fetchNextQuestion(concept.concept_id);
  };

  const fetchNextQuestion = async (conceptId: string) => {
    setIsGenerating(true);
    setGenerateError(null);
    setPracticeQuestion(null);
    setAttemptResult(null);
    setCurrentAnswer(null);
    setSubmitError(null);

    try {
      const q = await generatePractice({
        student_id: studentId || "",
        concept_id: conceptId,
        subject: "Science",
      });
      setPracticeQuestion(q);
      setPracticeCount((c) => c + 1);
    } catch (err: unknown) {
      console.error("Practice Gen Error:", err);
      const e = err as Error;
      setGenerateError(e.message || "Failed to generate practice question.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = async () => {
    if (!currentAnswer || !practiceQuestion || isSubmitting) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const res = await submitPracticeAttempt({
        student_id: studentId || "",
        question_id: practiceQuestion.question_id,
        student_answer: currentAnswer,
        hint_used: false,
      });

      setAttemptResult(res);
      
      // Update local concept mastery so if we go back, it's accurate
      setDashboardData(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          concepts: prev.concepts.map(c => 
            c.concept_id === selectedConcept?.concept_id
              ? { ...c, score: res.mastery_score, attempts: c.attempts + 1 }
              : c
          )
        };
      });

      if (selectedConcept) {
        setSelectedConcept({ ...selectedConcept, score: res.mastery_score, attempts: selectedConcept.attempts + 1 });
      }

    } catch (err: unknown) {
      console.error("Practice Attempt Error:", err);
      const e = err as Error;
      setSubmitError(e.message || "Failed to submit answer.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackToConcepts = () => {
    setSelectedConcept(null);
    setPracticeQuestion(null);
    setAttemptResult(null);
    setCurrentAnswer(null);
    setPracticeCount(0);
  };

  return (
    <main className="p-4 md:p-8 max-w-5xl mx-auto min-h-[calc(100vh-65px)]">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-2">
          <Brain className="h-8 w-8 text-primary" />
          Adaptive Practice
        </h1>
        <p className="text-muted-foreground text-base">
          Master your subjects with AI-driven questions tailored to your level.
        </p>
      </div>

      <AnimatePresence mode="wait">
        {!selectedConcept ? (
          /* PHASE 1: CONCEPT SELECTION */
          <motion.div
            key="concept-selection"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {isLoadingConcepts ? (
              <div className="py-12 flex flex-col items-center justify-center space-y-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-muted-foreground font-medium">Loading your mastery profile...</p>
              </div>
            ) : conceptsError ? (
              <div className="px-5 py-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-900 font-medium flex items-center gap-3">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                {conceptsError}
              </div>
            ) : dashboardData?.concepts && dashboardData.concepts.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData.concepts.map((concept) => (
                  <Card 
                    key={concept.concept_id} 
                    className="cursor-pointer hover:border-primary hover:shadow-md transition-all group overflow-hidden"
                    onClick={() => startPractice(concept)}
                  >
                    <CardHeader className="pb-3 border-b bg-muted/20">
                      <CardTitle className="text-lg font-bold group-hover:text-primary transition-colors line-clamp-1">
                        {concept.concept_name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-4">
                      <div>
                        <div className="flex justify-between text-xs font-medium text-muted-foreground mb-1.5">
                          <span>Mastery</span>
                          <span>{Math.round(concept.score * 100)}%</span>
                        </div>
                        <div className="relative h-2 rounded-full bg-muted overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-300 bg-primary"
                            style={{ width: `${Math.round(concept.score * 100)}%` }}
                          />
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{concept.attempts} {concept.attempts === 1 ? 'attempt' : 'attempts'}</span>
                        <div className="flex items-center text-primary font-medium opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0">
                          Practice <ChevronLeft className="h-3 w-3 rotate-180 ml-0.5" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="py-12 flex flex-col items-center justify-center text-center max-w-md mx-auto">
                <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mb-4">
                  <BookOpen className="h-8 w-8 text-muted-foreground/60" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Concepts Found</h3>
                <p className="text-muted-foreground mb-6">
                  You haven&apos;t asked any doubts yet, so we don&apos;t have any concepts for you to practice. 
                  Ask your first doubt to unlock adaptive practice!
                </p>
                <Button nativeButton={false} render={<Link href="/ask" />} className="gap-2">
                  <Sparkles className="h-4 w-4" />
                  Ask a Doubt
                </Button>
              </div>
            )}
          </motion.div>
        ) : (
          /* PHASE 2: PRACTICE LOOP */
          <motion.div
            key="practice-loop"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="max-w-2xl mx-auto space-y-6"
          >
            <Button 
              variant="ghost" 
              onClick={handleBackToConcepts}
              className="pl-0 gap-2 hover:bg-transparent hover:text-primary -ml-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Back to Concepts
            </Button>

            <Card className="border-border bg-card shadow-sm">
              <CardHeader className="pb-3 border-b bg-muted/30">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-widest text-primary mb-1 block">
                      Topic
                    </span>
                    <CardTitle className="text-lg">{selectedConcept.concept_name}</CardTitle>
                  </div>
                  <span className="text-xs font-semibold text-muted-foreground bg-background border px-2.5 py-1 rounded-full whitespace-nowrap">
                    Q {practiceCount}
                  </span>
                </div>
              </CardHeader>

              <CardContent className="pt-6 pb-6">
                {isGenerating ? (
                  <div className="py-12 flex flex-col items-center justify-center space-y-4">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground font-medium">
                      Generating optimal question...
                    </p>
                  </div>
                ) : generateError ? (
                  <div className="px-5 py-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-900 font-medium flex items-center justify-center gap-3">
                    <AlertCircle className="h-5 w-5 flex-shrink-0" />
                    {generateError}
                  </div>
                ) : practiceQuestion ? (
                  <div className="space-y-6">
                    <div className="flex items-start justify-between gap-4">
                      <p className="text-[15px] font-medium leading-relaxed">
                        {practiceQuestion.question_text}
                      </p>
                      <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground bg-muted px-2 py-1 rounded-md shrink-0">
                        {practiceQuestion.difficulty}
                      </span>
                    </div>

                    {practiceQuestion.options && practiceQuestion.options.length > 0 && (
                      <div className="space-y-2.5">
                        {practiceQuestion.options.map((opt, idx) => {
                          const optionId = String.fromCharCode(97 + idx); // a, b, c, d
                          return (
                            <McqOption
                              key={idx}
                              id={optionId}
                              label={opt}
                              selected={currentAnswer === opt}
                              submitted={attemptResult !== null}
                              isCorrect={(attemptResult?.correct ?? false) && currentAnswer === opt}
                              onClick={() => !attemptResult && setCurrentAnswer(opt)}
                            />
                          );
                        })}
                      </div>
                    )}
                    
                    {submitError && (
                      <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 text-sm font-medium">
                        {submitError}
                      </div>
                    )}

                    {attemptResult && (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-4 pt-2"
                      >
                        <div className="space-y-3">
                          {attemptResult.correct ? (
                            <div className="px-4 py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-sm font-semibold">
                              ✓ Correct!
                            </div>
                          ) : (
                            <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm">
                              <span className="font-semibold block mb-1">Incorrect</span>
                              Review the feedback below.
                            </div>
                          )}
                          <div className="p-4 bg-muted/40 rounded-lg border border-border text-[13px] leading-relaxed text-foreground/90 shadow-inner">
                            {attemptResult.feedback}
                          </div>
                        </div>

                        {/* Updated Mastery */}
                        <div className="pt-4 border-t border-border mt-4">
                          <MasteryBar 
                            fromScore={selectedConcept.score} 
                            toScore={attemptResult.mastery_score} 
                          />
                        </div>
                      </motion.div>
                    )}

                    <div className="pt-2">
                      {!attemptResult ? (
                        <Button
                          onClick={handleSubmit}
                          disabled={!currentAnswer || isSubmitting}
                          className="w-full h-11 text-sm font-semibold"
                        >
                          {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : "Submit Answer"}
                        </Button>
                      ) : (
                        <Button
                          onClick={() => fetchNextQuestion(selectedConcept.concept_id)}
                          className="w-full h-11 text-sm font-semibold gap-2"
                        >
                          Next Question <ChevronLeft className="h-4 w-4 rotate-180" />
                        </Button>
                      )}
                    </div>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
