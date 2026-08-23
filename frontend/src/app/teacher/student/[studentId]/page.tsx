"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion, type Variants } from "motion/react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  User,
  GraduationCap,
  Globe,
  AlertTriangle,
  CheckCircle2,
  Brain,
  Lightbulb,
  Loader2,
  AlertCircle,
  BarChart,
  Target,
} from "lucide-react";

import { getStudentInsights } from "@/lib/api/teacher";
import type { StudentDetailResponse, TeacherInsight } from "@/types/api";

export default function TeacherStudentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const studentId = typeof params.studentId === "string" ? params.studentId : "";

  const [studentData, setStudentData] = useState<StudentDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchInsights() {
      if (!studentId) return;
      try {
        const data = await getStudentInsights(studentId);
        setStudentData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load student insights. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    fetchInsights();
  }, [studentId]);

  if (!studentId) {
    return (
      <div className="p-8 text-center text-red-500 mt-10">
        Invalid student ID.
      </div>
    );
  }

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
        <Button variant="outline" className="mt-4" onClick={() => router.back()}>
          Go Back
        </Button>
      </div>
    );
  }

  if (!studentData) {
    return (
      <div className="p-8 text-center text-muted-foreground mt-10">
        Student profile not found.
      </div>
    );
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

  const getStatusBadgeStyles = (status: string) => {
    switch (status) {
      case "at_risk":
        return "border-red-500 text-red-600 bg-red-500/10 font-bold uppercase text-[10px]";
      case "needs_attention":
        return "border-amber-500 text-amber-700 bg-amber-500/10 font-bold uppercase text-[10px]";
      case "improving":
        return "border-blue-500 text-blue-600 bg-blue-500/10 font-bold uppercase text-[10px]";
      case "on_track":
        return "border-emerald-500 text-emerald-600 bg-emerald-500/10 font-bold uppercase text-[10px]";
      default:
        return "border-muted-foreground text-muted-foreground bg-muted font-bold uppercase text-[10px]";
    }
  };

  const formatText = (text: string) => {
    return text.replace(/_/g, " ");
  };

  return (
    <motion.main
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-4xl mx-auto px-6 py-8 space-y-8 pb-20"
    >
      <motion.div variants={itemVariants}>
        <Link href="/teacher/dashboard">
          <Button variant="ghost" className="gap-2 text-muted-foreground pl-0 hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </motion.div>

      {/* Student Profile Header */}
      <motion.div
        variants={itemVariants}
        className="rounded-2xl border border-border bg-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xs"
      >
        <div className="flex items-center gap-5">
          <div className="h-16 w-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0">
            <User className="h-7 w-7 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              Student <span className="text-muted-foreground text-lg font-mono">#{studentData.student_id.split("-")[0]}</span>
            </h1>
            <div className="flex items-center gap-4 mt-1.5 text-sm font-medium text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <GraduationCap className="h-4 w-4" />
                Class {studentData.grade}
              </span>
              <span className="flex items-center gap-1.5">
                <Globe className="h-4 w-4" />
                Language: {studentData.preferred_language.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="space-y-4">
        <h2 className="text-xl font-bold tracking-tight">Detailed Concept Insights</h2>

        {studentData.insights.length === 0 ? (
          <div className="p-12 text-center text-muted-foreground border border-dashed border-border rounded-xl bg-card">
            <CheckCircle2 className="h-10 w-10 mx-auto text-muted-foreground/40 mb-4" />
            <h3 className="font-semibold text-lg text-foreground mb-1">No Practice Data</h3>
            <p className="max-w-sm mx-auto">This student hasn&apos;t completed enough practice attempts to generate insights yet.</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {studentData.insights.map((insight: TeacherInsight, index) => (
              <Card key={`${insight.concept_id}-${index}`} className="border-border bg-card overflow-hidden shadow-xs">
                <CardHeader className="pb-3 pt-5 border-b border-border bg-muted/20">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-1">
                      <h3 className="font-bold text-lg text-foreground">{insight.concept_name}</h3>
                      <div className="flex items-center gap-4 text-xs font-semibold text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Target className="h-3.5 w-3.5" />
                          Mastery: {Math.round(insight.mastery_score * 100)}%
                        </span>
                        {insight.recent_accuracy !== undefined && insight.recent_accuracy !== null && (
                          <span className="flex items-center gap-1">
                            <BarChart className="h-3.5 w-3.5" />
                            Recent Accuracy: {Math.round(insight.recent_accuracy * 100)}%
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          Errors: {insight.consecutive_errors}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex flex-row sm:flex-col items-center sm:items-end gap-2">
                      <Badge variant="outline" className={getStatusBadgeStyles(insight.status)}>
                        {formatText(insight.status)}
                      </Badge>
                      <span className="text-xs font-mono font-medium text-foreground bg-background px-2 py-0.5 rounded border border-border">
                        Trend: {formatText(insight.trend)}
                      </span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="p-6 space-y-5">
                  {/* Gap Analysis */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-secondary">
                      <Brain className="h-4 w-4" />
                      <span>Identified Learning Gap / Analysis</span>
                    </div>
                    <p className="text-sm leading-relaxed text-foreground bg-secondary/5 p-4 rounded-xl border border-secondary/20">
                      {insight.reason}
                    </p>
                  </div>

                  {/* Intervention */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary">
                      <Lightbulb className="h-4 w-4" />
                      <span>Recommended Classroom Intervention</span>
                    </div>
                    <div className="p-4 rounded-xl border border-primary/30 bg-primary/10 text-sm text-foreground leading-relaxed">
                      {insight.recommended_action}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </motion.div>
    </motion.main>
  );
}
