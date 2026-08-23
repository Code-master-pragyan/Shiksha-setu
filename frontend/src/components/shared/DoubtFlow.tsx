"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "motion/react";

import {
  getNoMatchFallback,
  type BilingualText,
} from "@/lib/formatters";
import { askDoubt } from "@/lib/api/doubt";
import { generatePractice, submitPracticeAttempt } from "@/lib/api/practice";
import { useAuthStore } from "@/lib/store/auth";
import {
  type DoubtResponse,
  type PracticeGenerateResponse,
  type PracticeAttemptResponse,
} from "@/types/api";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MasteryBar, McqOption } from "./PracticeUI";

import {
  BookOpen,
  Brain,
  LogIn,
  Sparkles,
  RotateCcw,
  Library,
  Loader2,
  SendHorizontal,
  User,
  Upload,
  Clipboard,
  Atom,
  AlertCircle,
  BarChart3,
  HelpCircle,
} from "lucide-react";

// ─────────────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────────────

export interface DoubtFlowProps {
  /** Controls mode-specific UI (guest shows login CTA, student skips it). */
  mode: "guest" | "student";
  /** Starting mastery score [0–1] for the concept being explored. */
  initialMasteryScore?: number;
  /** Called with the mastery delta after the session completes. */
  onComplete?: (delta: number) => void;
}

type Phase = "select" | "thinking" | "result";
type Lang = "en" | "as";


// ─────────────────────────────────────────────────────────────────────────────


// ─────────────────────────────────────────────────────────────────────────────
// TOP BAR
// ─────────────────────────────────────────────────────────────────────────────

function TopBar({ lang, mode }: { lang: Lang; mode: "guest" | "student" }) {
  const pathname = usePathname();

  const navLinks = [
    { href: "/student/dashboard", label: lang === "en" ? "Dashboard" : "ড্যাশব’ৰ্ড", icon: BarChart3 },
    { href: "/ask", label: lang === "en" ? "Ask Doubt" : "সন্দেহ সোধক", icon: HelpCircle },
    { href: "/student/practice", label: lang === "en" ? "Practice" : "অনুশীলন", icon: BookOpen },
    { href: "/student/progress", label: lang === "en" ? "Progress" : "অগ্ৰগতি", icon: Brain },
  ];

  return (
    <div className="border-b border-border bg-background sticky top-0 z-20 w-full">
      <div className="w-full px-6 py-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="font-semibold text-sm tracking-tight text-foreground flex items-center gap-1.5 hover:opacity-80 transition-opacity"
          >
            <Sparkles className="h-4 w-4 text-primary" />
            <span>ShikshaSetu AI</span>
          </Link>

          {mode === "student" && (
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const active = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={cn(
                      "px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors",
                      active
                        ? "bg-primary/20 text-foreground border border-primary/40"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    <span>{link.label}</span>
                  </Link>
                );
              })}
            </nav>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/student/profile"
            aria-label="Profile"
            className="h-8 w-8 rounded-full border border-border bg-muted flex items-center justify-center text-foreground hover:bg-primary/20 hover:border-primary transition-colors"
          >
            <User className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}



// ─────────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

export function DoubtFlow({
  mode,
  initialMasteryScore = 0,
  onComplete,
}: DoubtFlowProps) {
  const noMatchFallback = getNoMatchFallback();

  // ── Core state ──────────────────────────────────────────────────────────────
  const [lang] = useState<Lang>("en");
  const studentId = useAuthStore(state => state.studentId);
  const [phase, setPhase] = useState<Phase>("select");
  const [freeText, setFreeText] = useState("");
  const [noMatch, setNoMatch] = useState(false);
  
  const [doubtResponse, setDoubtResponse] = useState<DoubtResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Progressive reveal flags (result phase) ──────────────────────────────
  const [showExplanation, setShowExplanation] = useState(false);
  const [showPractice, setShowPractice] = useState(false);
  const [showMastery, setShowMastery] = useState(false);

  // ── Practice ─────────────────────────────────────────────────────────────
  const [practiceQuestion, setPracticeQuestion] = useState<PracticeGenerateResponse | null>(null);
  const [isGeneratingPractice, setIsGeneratingPractice] = useState(false);
  const [practiceCurrentAnswer, setPracticeCurrentAnswer] = useState<string | null>(null);
  const [isSubmittingPractice, setIsSubmittingPractice] = useState(false);
  const [practiceAttemptResult, setPracticeAttemptResult] = useState<PracticeAttemptResponse | null>(null);
  const [practiceError, setPracticeError] = useState<string | null>(null);
  const [practiceCount, setPracticeCount] = useState(0);

  // ── Mastery ───────────────────────────────────────────────────────────────
  const [finalScore, setFinalScore] = useState(initialMasteryScore);

  // ── Helper: bilingual text accessor ─────────────────────────────────────
  function tx(text: BilingualText): string {
    return text[lang];
  }

  // ── Reset all state to initial select phase ───────────────────────────────
  function resetAll() {
    setPhase("select");
    setDoubtResponse(null);
    setError(null);
    setFreeText("");
    setNoMatch(false);
    setShowExplanation(false);
    setShowPractice(false);
    setShowMastery(false);
    
    setPracticeQuestion(null);
    setIsGeneratingPractice(false);
    setPracticeCurrentAnswer(null);
    setIsSubmittingPractice(false);
    setPracticeAttemptResult(null);
    setPracticeError(null);
    setPracticeCount(0);
    
    setFinalScore(initialMasteryScore);
  }

  // ── Free text: Call backend API directly ────────
  async function handleFreeTextSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = freeText.trim();
    if (!q || isSubmitting) return;

    setIsSubmitting(true);
    setNoMatch(false);
    setError(null);
    setPhase("thinking");

    try {
      const response = await askDoubt({
        student_id: mode === "student" ? (studentId || "guest") : undefined,
        question: q,
        grade: 8,
        subject: "Science",
        preferred_language: lang === "en" ? "English" : "Assamese",
        top_k: 3,
      });

      setDoubtResponse(response);
      setPhase("result");
      setShowExplanation(true);
      setShowPractice(false);
      setShowMastery(false);
      
      // Also reset practice state if they ask a new doubt
      setPracticeQuestion(null);
      setPracticeAttemptResult(null);
      setPracticeError(null);
      setPracticeCurrentAnswer(null);
    } catch (err: unknown) {
      console.error("API Error:", err);
      const e = err as Error;
      setError(
        e.message || 
        (lang === "en" ? "Failed to get an answer. Please try again." : "উত্তৰ পাবলৈ বিফল। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।")
      );
      setPhase("select");
    } finally {
      setIsSubmitting(false);
    }
  }

  // ── Practice generation ───────────────────────────────────────────────────
  async function handleStartPractice() {
    setIsGeneratingPractice(true);
    setPracticeError(null);
    setPracticeQuestion(null);
    setPracticeAttemptResult(null);
    setPracticeCurrentAnswer(null);
    setShowPractice(true);
    setShowMastery(false);

    try {
      if (!doubtResponse?.concept_id) {
        throw new Error(lang === "en" ? "Practice is not available for this specific question." : "এই নিৰ্দিষ্ট প্ৰশ্নটোৰ বাবে অনুশীলন উপলব্ধ নহয়।");
      }

      const q = await generatePractice({
        student_id: mode === "student" ? (studentId || "guest") : "guest",
        concept_id: doubtResponse.concept_id,
        subject: "Science",
      });
      setPracticeQuestion(q);
      setPracticeCount((c) => c + 1);
    } catch (err: unknown) {
      console.error("Practice Gen Error:", err);
      const e = err as Error;
      setPracticeError(
        e.message || (lang === "en" ? "Failed to generate practice." : "অনুশীলন প্ৰস্তুত কৰিবলৈ বিফল।")
      );
    } finally {
      setIsGeneratingPractice(false);
    }
  }

  // ── Practice submission ───────────────────────────────────────────────────
  async function handlePracticeSubmit() {
    if (!practiceCurrentAnswer || !practiceQuestion || isSubmittingPractice) return;
    
    setIsSubmittingPractice(true);
    setPracticeError(null);

    try {
      const res = await submitPracticeAttempt({
        student_id: mode === "student" ? (studentId || "guest") : "guest",
        question_id: practiceQuestion.question_id,
        student_answer: practiceCurrentAnswer,
        hint_used: false,
      });
      
      setPracticeAttemptResult(res);
      setFinalScore(res.mastery_score);
      setShowMastery(true);
      if (onComplete) {
        onComplete(res.mastery_score - initialMasteryScore);
      }
    } catch (err: unknown) {
      console.error("Practice Attempt Error:", err);
      const e = err as Error;
      setPracticeError(
        e.message || (lang === "en" ? "Failed to submit answer." : "উত্তৰ দাখিল কৰিবলৈ বিফল।")
      );
    } finally {
      setIsSubmittingPractice(false);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-background font-sans text-foreground overflow-x-hidden relative flex flex-col">
      {/* Permanent Ambient Background Grid & Glows - Instant Render */}
      <div className="absolute inset-0 bg-[radial-gradient(#C5C984_1.5px,transparent_1.5px)] [background-size:24px_24px] opacity-65 pointer-events-none z-0" />
      <div className="absolute top-1/4 -left-24 w-[450px] h-[450px] bg-primary/25 rounded-full blur-[100px] pointer-events-none z-0" />
      <div className="absolute bottom-1/4 -right-24 w-[450px] h-[450px] bg-secondary/25 rounded-full blur-[100px] pointer-events-none z-0" />

      {/* Persistent Floating Science Watermarks */}
      <div className="hidden md:block absolute top-28 left-[10%] text-foreground/15 pointer-events-none z-0">
        <Atom className="h-16 w-16 animate-pulse" />
      </div>

      <div className="hidden md:block absolute top-36 right-[10%] text-foreground/15 pointer-events-none z-0">
        <Brain className="h-16 w-16 animate-pulse" />
      </div>

      <div className="hidden md:block absolute bottom-28 left-[12%] text-foreground/15 pointer-events-none z-0">
        <BookOpen className="h-14 w-14 animate-pulse" />
      </div>

      <div className="hidden md:block absolute bottom-32 right-[12%] text-foreground/15 pointer-events-none z-0">
        <Sparkles className="h-14 w-14 animate-pulse" />
      </div>

      {/* Persistent Top Navbar - Zero Delay */}
      <div className="relative z-10">
        <TopBar lang={lang} mode={mode} />
      </div>

      <div className="flex-1 flex flex-col relative z-10">
        <AnimatePresence mode="wait" initial={false}>
          {/* SELECT PHASE */}
          {phase === "select" && (
            <motion.div
              key="select"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="flex-1 flex flex-col items-center justify-center max-w-2xl w-full mx-auto px-5 -mt-12 pb-16"
            >
              {/* Hero text */}
              <div className="mb-8 text-center w-full">
                <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full border border-border bg-muted text-muted-foreground text-xs font-medium mb-4">
                  <Sparkles className="h-3.5 w-3.5 text-primary" />
                  {lang === "en" ? "AI-powered doubt solving" : "AI-চালিত সন্দেহ সমাধান"}
                </div>
                <h1 className="text-4xl font-bold tracking-tight mb-3">
                  {lang === "en" ? "What's your doubt?" : "আপোনাৰ সন্দেহ কি?"}
                </h1>
                <p className="text-muted-foreground text-base">
                  {lang === "en"
                    ? "Type your question below to get instant AI help"
                    : "তাতক্ষণিক AI সহায়ৰ বাবে তলত আপোনাৰ প্ৰশ্ন লিখক"}
                </p>
              </div>

              {/* Quick Actions (Upload & Link) */}
              <div className="grid grid-cols-2 gap-4 w-full max-w-xl mb-5">
                <motion.button
                  type="button"
                  whileHover={{ y: -3, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.accept = "image/*,.pdf,.doc,.docx,.mp3,.mp4";
                    input.onchange = (e) => {
                      const file = (e.target as HTMLInputElement).files?.[0];
                      if (file) {
                        setFreeText(`[Uploaded: ${file.name}]`);
                      }
                    };
                    input.click();
                  }}
                  className="p-4 rounded-2xl border border-border bg-card hover:border-primary hover:bg-muted/40 transition-all text-left flex flex-col justify-between cursor-pointer group shadow-xs"
                >
                  <div className="h-9 w-9 rounded-xl bg-muted/60 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <Upload className="h-5 w-5 text-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div className="mt-4">
                    <p className="font-semibold text-sm text-foreground">
                      {lang === "en" ? "Upload" : "আপলোড"}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {lang === "en" ? "File, audio, video" : "ফাইল, অডিঅ', ভিডিঅ'"}
                    </p>
                  </div>
                </motion.button>

                <motion.button
                  type="button"
                  whileHover={{ y: -3, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={async () => {
                    try {
                      const text = await navigator.clipboard.readText();
                      if (text) {
                        setFreeText(text);
                      }
                    } catch {
                      const pasted = prompt(
                        lang === "en" ? "Paste text here:" : "ইয়াত পাঠ পেষ্ট কৰক:"
                      );
                      if (pasted) {
                        setFreeText(pasted);
                      }
                    }
                  }}
                  className="p-4 rounded-2xl border border-border bg-card hover:border-primary hover:bg-muted/40 transition-all text-left flex flex-col justify-between cursor-pointer group shadow-xs"
                >
                  <div className="h-9 w-9 rounded-xl bg-muted/60 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <Clipboard className="h-5 w-5 text-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div className="mt-4">
                    <p className="font-semibold text-sm text-foreground">
                      {lang === "en" ? "Paste" : "পেষ্ট"}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {lang === "en" ? "Copied Text" : "কপি কৰা পাঠ"}
                    </p>
                  </div>
                </motion.button>
              </div>

              {/* Free-text input */}
              <form onSubmit={handleFreeTextSubmit} className="relative w-full max-w-xl">
                <input
                  type="text"
                  value={freeText}
                  onChange={(e) => { setFreeText(e.target.value); setNoMatch(false); }}
                  placeholder={
                    lang === "en"
                      ? "Type your question here…"
                      : "ইয়াত আপোনাৰ প্ৰশ্ন লিখক…"
                  }
                  className="w-full px-5 py-3.5 pr-14 rounded-xl border border-input bg-card text-base placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring shadow-xs"
                />
                <motion.button
                  type="submit"
                  disabled={isSubmitting || !freeText.trim()}
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.92 }}
                  aria-label={lang === "en" ? "Ask question" : "প্ৰশ্ন সোধক"}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 h-8.5 w-10 px-0 justify-center flex items-center bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-all shadow-xs disabled:opacity-50"
                >
                  <SendHorizontal className="h-4 w-4" />
                </motion.button>
              </form>

              {/* No-match fallback */}
              {noMatch && (
                <div className="mt-4 w-full max-w-xl px-4 py-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-900 font-medium text-sm leading-relaxed text-center">
                  {tx(noMatchFallback)}
                </div>
              )}

              {/* Error fallback */}
              {error && (
                <div className="mt-4 w-full max-w-xl px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-900 font-medium text-sm leading-relaxed flex items-center justify-center gap-2">
                  <AlertCircle className="h-4 w-4 flex-shrink-0" />
                  {error}
                </div>
              )}
            </motion.div>
          )}

        {/* THINKING PHASE */}
        {phase === "thinking" && (
          <motion.div
            key="thinking"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="min-h-screen flex flex-col items-center justify-center gap-5 p-6"
          >
            <div className="relative flex items-center justify-center">
              <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
              <div className="h-16 w-16 rounded-2xl bg-card border border-border shadow-xs flex items-center justify-center relative z-10">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            </div>
            <div className="text-center space-y-1.5 max-w-sm">
              <p className="font-bold text-lg text-foreground">
                {lang === "en" ? "Analyzing your doubt…" : "আপোনাৰ সন্দেহ বিশ্লেষণ কৰা হৈছে…"}
              </p>
              <p className="text-sm text-muted-foreground">
                {lang === "en" ? "Retrieving textbook evidence & generating explanation" : "পাঠ্যপুথিৰ তথ্য সংগ্ৰহ কৰি ব্যাখ্যা প্ৰস্তুত কৰা হৈছে"}
              </p>
            </div>
          </motion.div>
        )}

        {/* RESULT PHASE */}
        {phase === "result" && doubtResponse && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.35 }}
          >
            <div className="max-w-2xl mx-auto px-5 py-8 space-y-5 pb-24">
            {/* Selected doubt header */}
            <div className="flex items-start gap-3 px-4 py-3 rounded-lg bg-muted/40 border border-border">
              <Brain className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-0.5">
                  {lang === "en" ? "Your Doubt" : "আপোনাৰ সন্দেহ"}
                </p>
                <p className="text-sm font-medium leading-snug">{doubtResponse.question}</p>
              </div>
            </div>



            {/* Explanation + Citation */}
            {showExplanation && (
              <Card className="border-border bg-card">
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                    <BookOpen className="h-3 w-3" />
                    {lang === "en" ? "Explanation" : "ব্যাখ্যা"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pb-4 space-y-4">
                  <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                    {doubtResponse.answer.replace(/\\n/g, '\n').split(/(\*\*.*?\*\*)/g).map((part, i) => {
                      if (part.startsWith('**') && part.endsWith('**')) {
                        return <strong key={i} className="font-bold">{part.slice(2, -2)}</strong>;
                      }
                      return <span key={i}>{part}</span>;
                    })}
                  </p>

                  {doubtResponse.citations && doubtResponse.citations.length > 0 && (
                    <div className="space-y-3 mt-4">
                      {doubtResponse.citations.map((cit, idx) => (
                        <div key={idx} className="rounded-lg border border-border bg-muted/30 overflow-hidden">
                          <div className="flex items-center gap-2 px-3.5 py-2 border-b border-border bg-muted/50">
                            <Library className="h-3 w-3 text-primary" />
                            <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                              {lang === "en" ? "Verified Source" : "যাচাই কৰা উৎস"}
                            </span>
                          </div>
                          <div className="px-3.5 py-3 font-mono text-xs space-y-1">
                            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                              <span className="font-semibold text-foreground not-italic">
                                {cit.source_title}
                              </span>
                              <span className="text-muted-foreground">—</span>
                              <span className="text-muted-foreground">{cit.chapter}</span>
                              {cit.section && (
                                <>
                                  <span className="text-muted-foreground">·</span>
                                  <span className="text-muted-foreground">{cit.section}</span>
                                </>
                              )}
                              <span className="text-muted-foreground">·</span>
                              <span className="text-muted-foreground">
                                pp.&nbsp;{cit.page_start}{cit.page_end !== cit.page_start ? `-${cit.page_end}` : ''}
                              </span>
                            </div>
                            <p className="text-muted-foreground/80 line-clamp-3 mt-1 text-[11px] font-sans">
                              &quot;{cit.citation_text}&quot;
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Start Practice Action */}
                  {!showPractice && (
                    <div className="pt-2">
                      {doubtResponse.concept_id ? (
                        <Button onClick={handleStartPractice} className="w-full gap-2">
                          <Brain className="h-4 w-4" />
                          {lang === "en" ? "Practice this concept" : "এই ধাৰণাটো অনুশীলন কৰক"}
                        </Button>
                      ) : (
                        <div className="px-4 py-3 rounded-lg bg-muted/50 border border-border text-muted-foreground text-sm text-center flex items-center justify-center gap-2">
                          <AlertCircle className="h-4 w-4" />
                          {lang === "en" ? "Adaptive practice is unavailable for this specific topic." : "এই নিৰ্দিষ্ট বিষয়টোৰ বাবে অনুশীলন উপলব্ধ নহয়।"}
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Practice Questions */}
            {showPractice && (
              <Card className="border-border bg-card">
                <CardHeader className="pb-2 pt-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                      <Brain className="h-3 w-3 text-primary" />
                      {lang === "en" ? "Practice" : "অনুশীলন"}
                    </CardTitle>
                    {practiceCount > 0 && (
                      <span className="text-[11px] font-medium text-muted-foreground ml-1 bg-muted px-2 py-0.5 rounded-full">
                        {lang === "en" ? "Q" : "প্ৰ"}{practiceCount}
                      </span>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="pb-4 space-y-3.5">
                  {isGeneratingPractice ? (
                    <div className="py-8 flex flex-col items-center justify-center space-y-3">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" />
                      <p className="text-sm text-muted-foreground">
                        {lang === "en" ? "Generating adaptive question..." : "প্ৰশ্ন প্ৰস্তুত কৰা হৈছে..."}
                      </p>
                    </div>
                  ) : practiceError ? (
                    <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-900 font-medium text-sm leading-relaxed flex items-center justify-center gap-2">
                      <AlertCircle className="h-4 w-4 flex-shrink-0" />
                      {practiceError}
                    </div>
                  ) : practiceQuestion ? (
                    <>
                      <div className="flex items-start justify-between gap-4">
                        <p className="text-sm font-medium leading-snug">
                          {practiceQuestion.question_text}
                        </p>
                        <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground bg-muted/50 px-2 py-1 rounded">
                          {practiceQuestion.difficulty}
                        </span>
                      </div>

                      {practiceQuestion.options && practiceQuestion.options.length > 0 && (
                        <div className="space-y-2">
                          {practiceQuestion.options.map((opt, idx) => {
                            const optionId = String.fromCharCode(97 + idx); // a, b, c, d
                            return (
                              <McqOption
                                key={idx}
                                id={optionId}
                                label={opt}
                                selected={practiceCurrentAnswer === opt}
                                submitted={practiceAttemptResult !== null}
                                isCorrect={(practiceAttemptResult?.correct ?? false) && practiceCurrentAnswer === opt}
                                onClick={() => !practiceAttemptResult && setPracticeCurrentAnswer(opt)}
                              />
                            );
                          })}
                        </div>
                      )}
                      
                      {practiceAttemptResult && (
                        <div className="space-y-3">
                          {practiceAttemptResult.correct ? (
                            <div className="px-4 py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-sm font-semibold">
                              ✓ {lang === "en" ? "Correct!" : "শুদ্ধ!"}
                            </div>
                          ) : (
                            <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm">
                              <span className="font-semibold block mb-1">
                                {lang === "en" ? "Incorrect" : "ভুল"}
                              </span>
                              {lang === "en"
                                ? "Review the concept and try another question."
                                : "ধাৰণাটো পৰীক্ষা কৰক আৰু আন এটা প্ৰশ্ন চেষ্টা কৰক।"}
                            </div>
                          )}
                          <div className="p-3 bg-muted/40 rounded-lg border border-border text-sm text-muted-foreground">
                            {practiceAttemptResult.feedback}
                          </div>
                        </div>
                      )}

                      {!practiceAttemptResult ? (
                        <Button
                          onClick={handlePracticeSubmit}
                          disabled={!practiceCurrentAnswer || isSubmittingPractice}
                          className="w-full disabled:opacity-50 h-9"
                        >
                          {isSubmittingPractice ? <Loader2 className="h-4 w-4 animate-spin" /> : (lang === "en" ? "Submit Answer" : "উত্তৰ দিয়ক")}
                        </Button>
                      ) : (
                        <Button
                          onClick={handleStartPractice}
                          className="w-full h-9"
                        >
                          {lang === "en" ? "Next Question →" : "পৰৱৰ্তী প্ৰশ্ন →"}
                        </Button>
                      )}
                    </>
                  ) : null}
                </CardContent>
              </Card>
            )}

            {/* Mastery Summary */}
            {showMastery && (
              <Card className="border-border bg-card">
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                    <Sparkles className="h-3 w-3 text-primary" />
                    {lang === "en" ? "Session Complete" : "সেশন সম্পূৰ্ণ হ'ল"}
                  </CardTitle>
                </CardHeader>

                <CardContent className="pb-5 space-y-5">
                  <div className="flex items-center gap-4 px-4 py-3 rounded-lg bg-muted/40 border border-border">
                    <div className="flex-1">
                      <p className="text-sm font-medium leading-snug">
                        {lang === "en" ? "Session Mastered" : "সেশন সম্পূৰ্ণ"}
                      </p>
                      <p className="text-sm text-muted-foreground leading-relaxed mt-1">
                        {lang === "en"
                          ? `You completed practice with a mastery score of ${Math.round(finalScore * 100)}%.`
                          : `আপুনি ${Math.round(finalScore * 100)}% দক্ষতাৰে অনুশীলন সম্পূৰ্ণ কৰিলে।`}
                      </p>
                    </div>
                  </div>

                  <MasteryBar
                    fromScore={initialMasteryScore}
                    toScore={finalScore}
                  />

                  <div className="h-px bg-border" />

                  {mode === "guest" ? (
                    <div className="flex items-center gap-4 flex-wrap">
                      <p className="flex-1 text-sm text-muted-foreground min-w-[160px]">
                        {lang === "en"
                          ? "Log in to save your progress and track mastery over time."
                          : "আপোনাৰ অগ্ৰগতি সংৰক্ষণ কৰিবলৈ আৰু দক্ষতা অনুসৰণ কৰিবলৈ লগ ইন কৰক।"}
                      </p>
                      <Link
                        href="/login"
                        className="flex-shrink-0 inline-flex items-center gap-2 h-9 px-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 text-sm font-medium transition-colors"
                      >
                        <LogIn className="h-3.5 w-3.5" />
                        {lang === "en" ? "Save progress — Log in" : "অগ্ৰগতি সংৰক্ষণ কৰক"}
                      </Link>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {lang === "en"
                        ? "Your mastery score has been updated."
                        : "আপোনাৰ দক্ষতা স্ক'ৰ আপডেট কৰা হৈছে।"}
                    </p>
                  )}

                  <Button
                    variant="outline"
                    onClick={resetAll}
                    className="w-full gap-2 h-9"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    {lang === "en" ? "Ask another question" : "আন এটা প্ৰশ্ন সোধক"}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </motion.div>
      )}
      </AnimatePresence>
    </div>
    </div>
  );
}
