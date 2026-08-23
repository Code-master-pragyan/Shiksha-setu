"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, type Variants } from "motion/react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Brain,
  Sparkles,
  SendHorizontal,
  TrendingUp,
  Award,
  CheckCircle2,
  ArrowRight,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { getStudentDashboard } from "@/lib/api/student";
import { StudentDashboardResponse } from "@/types/api";
import { useAuthStore } from "@/lib/store/auth";

export default function StudentDashboardPage() {
  const studentId = useAuthStore(state => state.studentId);
  const [dashboardData, setDashboardData] = useState<StudentDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        if (!studentId) {
          throw new Error("Student ID is missing from session.");
        }
        
        const data = await getStudentDashboard(studentId);
        setDashboardData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard data. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, [studentId]);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-500 flex flex-col items-center justify-center gap-2 mt-10">
        <AlertCircle className="h-6 w-6" />
        <p className="font-medium">{error}</p>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="p-8 text-center text-muted-foreground mt-10">
        Student profile not found.
      </div>
    );
  }

  const { student, overall_mastery, accuracy_rate, concepts } = dashboardData;
  const avgPct = Math.round(overall_mastery * 100);
  const accuracyPct = Math.round(accuracy_rate * 100);

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
      className="max-w-6xl mx-auto px-6 py-8 space-y-8 pb-20"
    >
      {/* Welcome Banner */}
      <motion.div
        variants={itemVariants}
        className="rounded-2xl border border-border bg-card p-6 md:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xs"
      >
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-border bg-muted text-xs font-semibold text-muted-foreground">
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            <span>Class {student.grade} {student.preferred_language === "as" ? "Assamese" : "Science"}</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {student.name}!
          </h1>
          <p className="text-sm text-muted-foreground max-w-xl leading-relaxed">
            You are currently at{" "}
            <span className="font-semibold text-foreground">{avgPct}% Mastery</span>.
            Solve more doubts and complete practice checks to improve your score!
          </p>
        </div>

        <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
          <Button nativeButton={false} render={<Link href="/ask" />} className="h-11 px-5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-semibold text-sm flex items-center gap-2.5 shadow-xs">
            <SendHorizontal className="h-4 w-4" />
            <span>Ask a New Doubt</span>
          </Button>
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Stat 1: Overall Mastery */}
        <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
          <Card className="border-border bg-card h-full">
            <CardContent className="pt-5 pb-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center flex-shrink-0">
                <TrendingUp className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Overall Mastery
                </p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-2xl font-bold tabular-nums">{avgPct}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stat 2: Practice Accuracy */}
        <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
          <Card className="border-border bg-card h-full">
            <CardContent className="pt-5 pb-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Accuracy Rate
                </p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-2xl font-bold tabular-nums">{accuracyPct}%</span>
                  <span className="text-xs text-muted-foreground">MCQ practice</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Main Grid: Concept Mastery */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 gap-8">
        {/* Concept Mastery Breakdown */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold tracking-tight flex items-center gap-2">
              <Award className="h-5 w-5 text-primary" />
              <span>Concept Mastery Breakdown</span>
            </h2>
            <Link
              href="/student/progress"
              className="text-xs font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
            >
              <span>View Full Analytics</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <Card className="border-border bg-card">
            <CardContent className="p-6 space-y-6">
              {concepts.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground text-sm">
                  <Brain className="h-8 w-8 mx-auto text-muted-foreground/50 mb-3" />
                  <p>You haven&apos;t practiced any concepts yet.</p>
                  <Link href="/ask" className="text-primary hover:underline mt-2 inline-block">
                    Ask a doubt to get started!
                  </Link>
                </div>
              ) : (
                concepts.map((item) => {
                  const scorePct = Math.round(item.score * 100);

                  return (
                    <div key={item.concept_id} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-foreground">
                            {item.concept_name}
                          </span>
                        </div>
                        <span className="font-bold tabular-nums text-primary">
                          {scorePct}%
                        </span>
                      </div>

                      {/* Progress Bar Track */}
                      <div className="h-2.5 rounded-full bg-muted overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${scorePct}%` }}
                          transition={{ duration: 0.8, ease: "easeOut" }}
                          className="h-full rounded-full bg-primary"
                        />
                      </div>

                      <div className="flex items-center justify-between text-xs text-muted-foreground pt-0.5">
                        <span>{item.attempts} Practice Attempts</span>
                        <span>
                          {item.last_attempt
                            ? `Last active: ${new Date(item.last_attempt).toLocaleDateString()}`
                            : "Never attempted"}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </motion.main>
  );
}
