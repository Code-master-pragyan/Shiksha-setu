"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, type Variants } from "motion/react";
import { getMasteryTier } from "@/lib/formatters";
import { useAuthStore } from "@/lib/store/auth";
import { getStudentDashboard, updateStudentProfile } from "@/lib/api/student";
import type { StudentDashboardResponse } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  User,
  GraduationCap,
  School,
  Languages,
  Award,
  Sparkles,
  CheckCircle2,
  Settings,
  ArrowLeft,
  Save,
  Volume2,
} from "lucide-react";

export default function StudentProfilePage() {
  const studentId = useAuthStore(state => state.studentId);
  const user = useAuthStore(state => state.user);
  const [dashboardData, setDashboardData] = useState<StudentDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [preferredLang, setPreferredLang] = useState<"en" | "as" | "hi">("en");
  const [explanationLevel, setExplanationLevel] = useState<"step" | "visual" | "concise">("step");
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    async function loadData() {
      if (!studentId) return;
      try {
        setIsLoading(true);
        const data = await getStudentDashboard(studentId);
        setDashboardData(data);
        setPreferredLang((data.student.preferred_language as "en" | "as" | "hi") || "en");
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [studentId]);

  if (isLoading || !user) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Loading profile...
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Student profile not found.
      </div>
    );
  }

  const avgScore = dashboardData.overall_mastery;
  const overallTier = getMasteryTier(avgScore);
  const avgPct = Math.round(avgScore * 100);

  async function handleSaveSettings(e: React.FormEvent) {
    e.preventDefault();
    if (!studentId) return;
    try {
      setIsSaving(true);
      await updateStudentProfile(studentId, { preferred_language: preferredLang });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  }

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.05,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 16 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 },
    },
  };

  return (
    <motion.main
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-4xl mx-auto px-6 py-8 space-y-8 pb-24"
    >
      {/* Top Back Navigation */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <Link
          href="/student/dashboard"
          className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Dashboard</span>
        </Link>
        <Badge variant="outline" className="text-xs font-mono">
          Student ID: {dashboardData.student.id}
        </Badge>
      </motion.div>

      {/* Header Profile Card */}
      <motion.div
        variants={itemVariants}
        className="rounded-3xl border border-border bg-card p-6 md:p-8 space-y-6 shadow-xs relative overflow-hidden"
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
          <div className="flex items-center gap-5">
            <div className="h-20 w-20 rounded-2xl bg-primary/15 border-2 border-primary flex items-center justify-center text-primary flex-shrink-0 shadow-xs">
              <User className="h-10 w-10" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2.5 flex-wrap">
                <h1 className="text-2xl font-extrabold tracking-tight">
                  {user.name}
                </h1>
                {overallTier && (
                  <Badge
                    variant="outline"
                    className="text-xs px-2.5 py-0.5 font-bold capitalize"
                    style={{ borderColor: overallTier.color, color: overallTier.color }}
                  >
                    {overallTier.label} ({avgPct}%)
                  </Badge>
                )}
              </div>
              <p className="text-xs font-semibold text-muted-foreground flex items-center gap-2 flex-wrap">
                <span className="flex items-center gap-1">
                  <GraduationCap className="h-3.5 w-3.5 text-primary" />
                  Class {dashboardData.student.grade} Science · Roll #8
                </span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <School className="h-3.5 w-3.5 text-secondary" />
                  Govt. HS School, Guwahati
                </span>
              </p>
            </div>
          </div>

          <Link href="/ask">
            <Button size="sm" className="h-10 px-4 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-semibold text-xs gap-2">
              <Sparkles className="h-4 w-4" />
              <span>Ask a Doubt</span>
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-border">
          <div className="p-3 rounded-xl bg-muted/40 text-center space-y-0.5">
            <p className="text-[10px] uppercase font-semibold text-muted-foreground">Mastery Score</p>
            <p className="text-lg font-extrabold text-foreground">{avgPct}%</p>
          </div>
          <div className="p-3 rounded-xl bg-muted/40 text-center space-y-0.5">
            <p className="text-[10px] uppercase font-semibold text-muted-foreground">Doubts Solved</p>
            <p className="text-lg font-extrabold text-foreground">12</p>
          </div>
          <div className="p-3 rounded-xl bg-muted/40 text-center space-y-0.5">
            <p className="text-[10px] uppercase font-semibold text-muted-foreground">Accuracy Rate</p>
            <p className="text-lg font-extrabold text-foreground">{Math.round(dashboardData.accuracy_rate * 100)}%</p>
          </div>
          <div className="p-3 rounded-xl bg-muted/40 text-center space-y-0.5">
            <p className="text-[10px] uppercase font-semibold text-muted-foreground">Streak</p>
            <p className="text-lg font-extrabold text-foreground">5 Days</p>
          </div>
        </div>
      </motion.div>

      {/* Main Grid: Learning Preferences & Badges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Learning Settings & Preferences (2 Cols) */}
        <motion.div variants={itemVariants} className="md:col-span-2 space-y-6">
          <Card className="border-border bg-card">
            <CardHeader className="border-b border-border pb-4">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Settings className="h-4 w-4 text-primary" />
                <span>Learning & AI Preferences</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <form onSubmit={handleSaveSettings} className="space-y-6">
                {/* Language Preference */}
                <div className="space-y-2">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Preferred AI Explanation Language
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    <button
                      type="button"
                      onClick={() => setPreferredLang("en")}
                      className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-between transition-all ${
                        preferredLang === "en"
                          ? "border-primary bg-primary/10 text-foreground"
                          : "border-border bg-background text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Languages className="h-4 w-4 text-primary" />
                        <span>English</span>
                      </div>
                      {preferredLang === "en" && <CheckCircle2 className="h-4 w-4 text-primary" />}
                    </button>

                    <button
                      type="button"
                      onClick={() => setPreferredLang("as")}
                      className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-between transition-all ${
                        preferredLang === "as"
                          ? "border-primary bg-primary/10 text-foreground"
                          : "border-border bg-background text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Languages className="h-4 w-4 text-primary" />
                        <span>অসমীয়া (Assamese)</span>
                      </div>
                      {preferredLang === "as" && <CheckCircle2 className="h-4 w-4 text-primary" />}
                    </button>
                    <button
                      type="button"
                      onClick={() => setPreferredLang("hi")}
                      className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-between transition-all ${
                        preferredLang === "hi"
                          ? "border-primary bg-primary/10 text-foreground"
                          : "border-border bg-background text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Languages className="h-4 w-4 text-primary" />
                        <span>हिंदी (Hindi)</span>
                      </div>
                      {preferredLang === "hi" && <CheckCircle2 className="h-4 w-4 text-primary" />}
                    </button>
                  </div>
                </div>

                {/* Explanation Detail Level */}
                <div className="space-y-2">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    AI Explanation Style
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { id: "step", label: "Step-by-Step", desc: "Detailed groundwork" },
                      { id: "visual", label: "Visual & Diagrams", desc: "Circuit diagrams" },
                      { id: "concise", label: "Concise Quick", desc: "Short summaries" },
                    ].map((style) => (
                      <button
                        key={style.id}
                        type="button"
                        onClick={() => setExplanationLevel(style.id as "step" | "visual" | "concise")}
                        className={`p-3 rounded-xl border text-left transition-all ${
                          explanationLevel === style.id
                            ? "border-primary bg-primary/10 text-foreground"
                            : "border-border bg-background text-muted-foreground hover:text-foreground"
                        }`}
                      >
                        <p className="text-xs font-bold">{style.label}</p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">{style.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Voice Assistance Toggle */}
                <div className="flex items-center justify-between p-3.5 rounded-xl border border-border bg-muted/30">
                  <div className="flex items-center gap-3">
                    <Volume2 className="h-5 w-5 text-secondary" />
                    <div>
                      <p className="text-xs font-bold">Voice Assistance & Audio Help</p>
                      <p className="text-[11px] text-muted-foreground">Read explanations out loud in preferred language</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setVoiceEnabled(!voiceEnabled)}
                    className={`px-3 py-1 rounded-full text-xs font-bold transition-colors ${
                      voiceEnabled ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground border border-border"
                    }`}
                  >
                    {voiceEnabled ? "Enabled" : "Disabled"}
                  </button>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <Button type="submit" disabled={isSaving} className="h-10 px-5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-semibold text-xs gap-2">
                    <Save className="h-4 w-4" />
                    <span>{isSaving ? "Saving..." : "Save Preferences"}</span>
                  </Button>
                  {savedSuccess && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1"
                    >
                      <CheckCircle2 className="h-4 w-4" />
                      Saved successfully!
                    </motion.span>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        {/* Badges & Achievements (1 Col) */}
        <motion.div variants={itemVariants} className="space-y-6">
          <Card className="border-border bg-card">
            <CardHeader className="border-b border-border pb-4">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Award className="h-4 w-4 text-secondary" />
                <span>Achievements & Badges</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              {/* Badge 1 */}
              <div className="flex items-center gap-3.5 p-3 rounded-xl border border-border bg-muted/30">
                <div className="h-10 w-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-600 font-bold text-lg flex-shrink-0">
                  ⚡
                </div>
                <div className="space-y-0.5">
                  <p className="text-xs font-bold text-foreground">5-Day Active Streak</p>
                  <p className="text-[10px] text-muted-foreground">Logged in and practiced 5 days in a row</p>
                </div>
              </div>

              {/* Badge 2 */}
              <div className="flex items-center gap-3.5 p-3 rounded-xl border border-border bg-muted/30">
                <div className="h-10 w-10 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center text-primary font-bold text-lg flex-shrink-0">
                  🔬
                </div>
                <div className="space-y-0.5">
                  <p className="text-xs font-bold text-foreground">First Doubt Resolved</p>
                  <p className="text-[10px] text-muted-foreground">Asked and understood open circuit topic</p>
                </div>
              </div>

              {/* Badge 3 */}
              <div className="flex items-center gap-3.5 p-3 rounded-xl border border-border bg-muted/30">
                <div className="h-10 w-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-600 font-bold text-lg flex-shrink-0">
                  💡
                </div>
                <div className="space-y-0.5">
                  <p className="text-xs font-bold text-foreground">Conductors Mastered</p>
                  <p className="text-[10px] text-muted-foreground">Reached 81% score in Conductors & Insulators</p>
                </div>
              </div>

              {/* Locked Badge */}
              <div className="flex items-center gap-3.5 p-3 rounded-xl border border-border bg-muted/10 opacity-60">
                <div className="h-10 w-10 rounded-xl bg-muted border border-border flex items-center justify-center text-muted-foreground font-bold text-sm flex-shrink-0">
                  🔒
                </div>
                <div className="space-y-0.5">
                  <p className="text-xs font-bold text-foreground">Science Scholar (Locked)</p>
                  <p className="text-[10px] text-muted-foreground">Reach 80%+ overall class mastery score</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.main>
  );
}
