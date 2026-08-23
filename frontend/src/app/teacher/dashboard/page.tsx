"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, type Variants } from "motion/react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  School,
  AlertTriangle,
  Users,
  TrendingUp,
  Sparkles,
  Lightbulb,
  CheckCircle2,
  FileText,
  Brain,
  Loader2,
  AlertCircle,
} from "lucide-react";

import { getTeacherInsights } from "@/lib/api/teacher";
import type { TeacherSummaryResponse } from "@/types/api";

export default function TeacherDashboardPage() {
  const [dashboardData, setDashboardData] = useState<TeacherSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchInsights() {
      try {
        const data = await getTeacherInsights({ grade: 8 }); // Hardcoding grade for demo
        setDashboardData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load teacher insights. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    fetchInsights();
  }, []);

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
        No insights found.
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

  const formatStatusText = (status: string) => {
    return status.replace("_", " ");
  };

  return (
    <motion.main
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-6xl mx-auto px-6 py-8 space-y-8 pb-20"
    >
      {/* Header Banner */}
      <motion.div
        variants={itemVariants}
        className="rounded-2xl border border-border bg-card p-6 md:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xs"
      >
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-border bg-muted text-xs font-semibold text-muted-foreground">
            <School className="h-3.5 w-3.5 text-primary" />
            <span>Class Overview</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Teacher Misconception & Diagnostic Hub
          </h1>
          <p className="text-sm text-muted-foreground max-w-xl leading-relaxed">
            AI-driven misconception pattern analysis & recommended targeted interventions based on recent student activity.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" className="h-10 px-4 text-xs font-semibold gap-2">
            <FileText className="h-4 w-4" />
            <span>Export Insights Report</span>
          </Button>
          <Button className="h-10 px-4 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-semibold text-xs flex items-center gap-2 shadow-xs">
            <Sparkles className="h-4 w-4" />
            <span>Generate Quiz</span>
          </Button>
        </div>
      </motion.div>

      {/* Top 4 Stat Cards based strictly on backend summaries */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stat 1: Total Students */}
        <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
          <Card className="border-border bg-card h-full">
            <CardContent className="pt-5 pb-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center flex-shrink-0">
                <Users className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Total Students
                </p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-2xl font-bold tabular-nums">{dashboardData.total_students}</span>
                  <span className="text-xs text-muted-foreground">Active in DB</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stat 2: At-Risk */}
        <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
          <Card className="border-border bg-card h-full">
            <CardContent className="pt-5 pb-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-red-500/15 border border-red-500/30 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  At-Risk
                </p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-2xl font-bold tabular-nums text-red-600 dark:text-red-400">
                    {dashboardData.at_risk}
                  </span>
                  <span className="text-xs text-muted-foreground">Require intervention</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stat 3: Needs Attention */}
        <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
          <Card className="border-border bg-card h-full">
            <CardContent className="pt-5 pb-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center flex-shrink-0">
                <Brain className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Needs Attention
                </p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-2xl font-bold tabular-nums text-amber-600 dark:text-amber-400">{dashboardData.needs_attention}</span>
                  <span className="text-xs text-muted-foreground">Struggling</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stat 4: On Track */}
        <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
          <Card className="border-border bg-card h-full">
            <CardContent className="pt-5 pb-5 flex items-center gap-4">
              <div className="h-11 w-11 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  On-Track
                </p>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-2xl font-bold tabular-nums text-emerald-600 dark:text-emerald-400">{dashboardData.on_track}</span>
                  <span className="text-xs text-muted-foreground">Performing well</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Main Grid: At-Risk Interventions (Spans full width as Class Analytics is unsupported) */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Active Insights */}
        <div id="at-risk" className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold tracking-tight flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-primary" />
              <span>Student Insights & AI Recommended Interventions</span>
            </h2>
            <span className="text-xs text-muted-foreground">
              Updated from latest student diagnostic attempts
            </span>
          </div>

          <div className="space-y-4">
            {dashboardData.insights.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground border border-dashed border-border rounded-xl">
                <CheckCircle2 className="h-8 w-8 mx-auto text-muted-foreground/50 mb-3" />
                <p>No actionable insights currently detected.</p>
              </div>
            ) : (
              dashboardData.insights.map((insight, index) => (
                <motion.div key={`${insight.student_id}-${index}`} whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
                  <Card className="border-border bg-card overflow-hidden shadow-xs">
                    <CardHeader className="pb-3 pt-5 border-b border-border bg-muted/20">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-base text-foreground">
                            Student: {insight.student_id.split("-")[0]}...
                          </span>
                          <Badge
                            variant="outline"
                            className={getStatusBadgeStyles(insight.status)}
                          >
                            {formatStatusText(insight.status)}
                          </Badge>
                        </div>
                        <span className="text-xs font-mono text-muted-foreground flex items-center gap-2">
                          <span className="font-semibold text-foreground">Trend: {insight.trend}</span>
                          <span className="opacity-50">|</span>
                          <span>Concept: {insight.concept_name}</span>
                        </span>
                      </div>
                    </CardHeader>

                    <CardContent className="p-6 space-y-4">
                      {/* Identified Misconception / Reason */}
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                          <Brain className="h-3.5 w-3.5 text-secondary" />
                          <span>Identified Learning Gap / Analysis</span>
                        </div>
                        <p className="text-sm leading-relaxed text-foreground bg-muted/30 p-3.5 rounded-xl border border-border">
                          {insight.reason}
                        </p>
                      </div>

                      {/* Recommended Action / Intervention */}
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary">
                          <Lightbulb className="h-3.5 w-3.5 text-primary" />
                          <span>Recommended Classroom Intervention</span>
                        </div>
                        <div className="p-3.5 rounded-xl border border-primary/30 bg-primary/10 text-sm text-foreground leading-relaxed">
                          {insight.recommended_action}
                        </div>
                      </div>

                      {/* Actions Bar */}
                      <div className="pt-2 flex items-center justify-between flex-wrap gap-2">
                        <div className="flex gap-4">
                          <span className="text-xs font-medium bg-muted px-2 py-1 rounded-md">
                            Score: {Math.round(insight.mastery_score * 100)}%
                          </span>
                          <span className="text-xs font-medium bg-muted px-2 py-1 rounded-md">
                            Consecutive Errors: {insight.consecutive_errors}
                          </span>
                        </div>
                        <Button nativeButton={false} render={<Link href={`/teacher/student/${insight.student_id}`} />} variant="outline" size="sm" className="text-xs gap-1.5">
                          <TrendingUp className="h-3.5 w-3.5 text-secondary" />
                          <span>View Full History</span>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </div>
        </div>

      </motion.div>
    </motion.main>
  );
}
