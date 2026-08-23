"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import { useAuthStore } from "@/lib/store/auth";
import { getStudentDashboard } from "@/lib/api/student";
import type { StudentDashboardResponse } from "@/types/api";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Brain, AlertCircle, BookOpen, Sparkles, TrendingUp, Target, ShieldCheck, Flame, ChevronRight } from "lucide-react";
import { MasteryBar } from "@/components/shared/PracticeUI";

export default function StudentProgressPage() {
  const studentId = useAuthStore(state => state.studentId);
  const [dashboardData, setDashboardData] = useState<StudentDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        setError(null);
        if (!studentId) {
          throw new Error("Student ID is missing from session.");
        }
        
        const data = await getStudentDashboard(studentId);
        setDashboardData(data);
      } catch (err: unknown) {
        console.error("Failed to load progress:", err);
        const e = err as Error;
        setError(e.message || "Failed to load your learning analytics. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [studentId]);

  if (isLoading) {
    return (
      <main className="p-4 md:p-8 max-w-5xl mx-auto min-h-[calc(100vh-65px)] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground font-medium">Analyzing learning progress...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-4 md:p-8 max-w-5xl mx-auto min-h-[calc(100vh-65px)]">
        <div className="px-5 py-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-900 font-medium flex items-center gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          {error}
        </div>
      </main>
    );
  }

  const hasData = dashboardData && dashboardData.concepts && dashboardData.concepts.length > 0;

  if (!hasData) {
    return (
      <main className="p-4 md:p-8 max-w-5xl mx-auto min-h-[calc(100vh-65px)] flex flex-col items-center justify-center text-center">
        <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mb-4">
          <Brain className="h-8 w-8 text-muted-foreground/60" />
        </div>
        <h3 className="text-xl font-bold mb-2">No learning data yet.</h3>
        <p className="text-muted-foreground mb-6 max-w-md">
          You haven&apos;t generated any learning data yet. Start by asking a doubt or completing a practice session!
        </p>
        <Link href="/ask">
          <Button className="gap-2">
            <Sparkles className="h-4 w-4" />
            Ask a Doubt
          </Button>
        </Link>
      </main>
    );
  }

  // Calculate presentation metrics
  const totalAttempts = dashboardData.concepts.reduce((sum, c) => sum + c.attempts, 0);
  
  // Sort concepts
  const strongestConcepts = [...dashboardData.concepts].sort((a, b) => b.score - a.score);
  // Need practice = bottom 50% or lowest score
  const needsPractice = [...dashboardData.concepts].sort((a, b) => a.score - b.score);

  return (
    <main className="p-4 md:p-8 max-w-5xl mx-auto min-h-[calc(100vh-65px)] space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-2">
          <TrendingUp className="h-8 w-8 text-primary" />
          Learning Analytics
        </h1>
        <p className="text-muted-foreground text-base">
          Track your real-time mastery and practice accuracy across all subjects.
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        {/* Overall Mastery */}
        <Card className="border-border bg-card shadow-sm">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                <ShieldCheck className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Overall Mastery</p>
                <div className="text-3xl font-bold mt-1">
                  {Math.round(dashboardData.overall_mastery * 100)}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Practice Accuracy */}
        <Card className="border-border bg-card shadow-sm">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-emerald-500/10 flex items-center justify-center">
                <Target className="h-6 w-6 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Practice Accuracy</p>
                <div className="text-3xl font-bold mt-1">
                  {Math.round(dashboardData.accuracy_rate * 100)}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Total Attempts */}
        <Card className="border-border bg-card shadow-sm">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-orange-500/10 flex items-center justify-center">
                <Flame className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Questions Attempted</p>
                <div className="text-3xl font-bold mt-1">
                  {totalAttempts}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-4">
        {/* Strongest Concepts */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="space-y-4"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-emerald-500" />
              Strongest Concepts
            </h2>
          </div>
          <div className="space-y-3">
            {strongestConcepts.slice(0, 3).map((concept) => (
              <Card key={concept.concept_id} className="border-border">
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-foreground line-clamp-1">{concept.concept_name}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{concept.attempts} attempts</p>
                    </div>
                  </div>
                  <MasteryBar fromScore={0} toScore={concept.score} />
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>

        {/* Needs Practice */}
        <motion.div
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="space-y-4"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Target className="h-5 w-5 text-orange-500" />
              Needs Practice
            </h2>
            <Link href="/student/practice">
              <Button variant="ghost" size="sm" className="h-8 text-primary">
                Practice Now <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </div>
          <div className="space-y-3">
            {needsPractice.slice(0, 3).map((concept) => (
              <Card key={concept.concept_id} className="border-border">
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-foreground line-clamp-1">{concept.concept_name}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{concept.attempts} attempts</p>
                    </div>
                  </div>
                  <MasteryBar fromScore={0} toScore={concept.score} />
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>
      </div>
      
      {/* All Concepts Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
        className="pt-6"
      >
        <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
          <BookOpen className="h-5 w-5 text-primary" />
          All Concepts Breakdown
        </h2>
        <Card className="border-border overflow-hidden">
          <div className="divide-y divide-border">
            {dashboardData.concepts.map((concept) => (
              <div key={concept.concept_id} className="p-4 md:p-5 flex flex-col md:flex-row md:items-center gap-4 justify-between hover:bg-muted/20 transition-colors">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-foreground truncate">{concept.concept_name}</h3>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1.5">
                    <span>{concept.attempts} {concept.attempts === 1 ? 'attempt' : 'attempts'}</span>
                    {concept.last_attempt && (
                      <>
                        <span className="w-1 h-1 rounded-full bg-muted-foreground/30" />
                        <span>Last active: {new Date(concept.last_attempt).toLocaleDateString()}</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="w-full md:w-48 shrink-0">
                  <div className="flex justify-between text-xs font-semibold mb-1.5">
                    <span className="text-muted-foreground">Mastery</span>
                    <span>{Math.round(concept.score * 100)}%</span>
                  </div>
                  <div className="relative h-2 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-300 bg-primary"
                      style={{ width: `${Math.round(concept.score * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>
    </main>
  );
}
