"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence, type Variants } from "motion/react";
import {
  Sparkles,
  ArrowRight,
  Brain,
  CheckCircle2,
  School,
  GraduationCap,
  ShieldCheck,
  AlertTriangle,
  ArrowUpRight,
  Library,
  Lightbulb,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type Lang = "en" | "as";
type ActiveTab = "rag" | "diagnostic" | "teacher";

export default function LandingPage() {
  const [lang] = useState<Lang>("en");
  const [activeTab, setActiveTab] = useState<ActiveTab>("rag");

  // Animation variants
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.12,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 24 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <div className="min-h-screen bg-background font-sans text-foreground flex flex-col overflow-x-hidden">
      {/* Top Navbar */}
      <header className="border-b border-border bg-background sticky top-0 z-30 w-full">
        <div className="w-full px-6 py-3.5 flex items-center justify-between gap-4">
          <Link
            href="/"
            className="font-semibold text-base tracking-tight text-foreground flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <Sparkles className="h-5 w-5 text-primary" />
            <span className="font-bold text-lg">ShikshaSetu AI</span>
          </Link>

          <div className="flex items-center gap-3">


            <Button nativeButton={false} render={<Link href="/login" />} size="sm" variant="outline" className="text-xs font-semibold h-8.5 px-3.5">
              {lang === "en" ? "Sign In" : "প্ৰৱেশ কৰক"}
            </Button>

            <Button nativeButton={false} render={<Link href="/ask" />} size="sm" className="text-xs font-semibold h-8.5 px-4 bg-primary text-primary-foreground hover:bg-primary/90">
              {lang === "en" ? "Try AI Doubt Solver" : "সন্দেহ সমাধান কৰক"}
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <motion.section
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="px-6 py-20 md:py-28 max-w-5xl mx-auto text-center space-y-8"
      >
        <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-border bg-card text-xs font-semibold text-foreground shadow-xs">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>
            {lang === "en"
              ? "Personalized Multilingual AI Learning Companion"
              : "ব্যক্তিগতকৃত বহુભাষিক AI শিক্ষাদান সংগী"}
          </span>
        </motion.div>

        <motion.h1
          variants={itemVariants}
          className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight max-w-4xl mx-auto text-foreground"
        >
          {lang === "en" ? (
            <>
              We don&apos;t personalize the answer. <br />
              <span className="text-primary underline underline-offset-8 decoration-secondary/60">
                We personalize the learning path.
              </span>
            </>
          ) : (
            <>
              আমি কেৱল উত্তৰ ব্যক্তিগত নকৰোঁ। <br />
              <span className="text-primary underline underline-offset-8 decoration-secondary/60">
                আমি শিকণৰ পথটোহে ব্যক্তিগত কৰোঁ।
              </span>
            </>
          )}
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-base md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed"
        >
          {lang === "en"
            ? "Connecting a student's specific confusion to grounded explanations, trusted textbook citations, misconception diagnostics, and adaptive practice."
            : "ছাত্ৰ-ছাত্ৰীৰ নিৰ্দষ্ট খেলিমেলি পোনপটীয়া সংৰক্ষিত ব্যাখ্যা, পাঠ্যপুথিৰ উৎস আৰু অভিযোজিত অনুশীলনৰ সৈতে সংযোগ কৰে।"}
        </motion.p>

        <motion.div variants={itemVariants} className="flex items-center justify-center gap-4 flex-wrap pt-4">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button nativeButton={false} render={<Link href="/ask" />} className="h-12 px-7 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-bold text-base flex items-center gap-2.5 shadow-xs">
              <span>{lang === "en" ? "Ask a Doubt Now" : "এতিয়াই প্ৰশ্ন সোধক"}</span>
              <ArrowRight className="h-5 w-5" />
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button nativeButton={false} render={<Link href="/login" />} variant="outline" className="h-12 px-7 rounded-xl font-bold text-base border-border bg-card hover:bg-muted">
              {lang === "en" ? "Login as Student / Teacher" : "লগ ইন কৰক"}
            </Button>
          </motion.div>
        </motion.div>
      </motion.section>

      {/* Interactive Human-Crafted Feature Showcase (NO MORE AI LOOKING CARDS) */}
      <section className="px-6 py-20 bg-card border-y border-border">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <Badge variant="outline" className="border-primary text-primary text-xs font-semibold px-3 py-0.5">
              Live System Preview
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight">
              {lang === "en" ? "Experience the Closed-Loop Engine" : "সম্পূৰ্ণ শিকাৰ ইঞ্জিন অভিজ্ঞতা লাভ কৰক"}
            </h2>
            <p className="text-muted-foreground text-sm max-w-lg mx-auto">
              {lang === "en"
                ? "Click through the 3 interactive stages below to see how ShikshaSetu turns student confusion into verified mastery."
                : "তলৰ ৩টা পৰ্যায়ত ক্লিক কৰি শিক্ষা সেতুৰ প্ৰকৃত পদ্ধতি পৰীক্ষা কৰক।"}
            </p>
          </div>

          {/* Interactive Feature Tabs */}
          <div className="flex items-center justify-center gap-2 p-1.5 rounded-2xl bg-muted border border-border max-w-2xl mx-auto flex-wrap">
            <button
              type="button"
              onClick={() => setActiveTab("rag")}
              className={`flex-1 py-3 px-4 rounded-xl text-xs md:text-sm font-semibold flex items-center justify-center gap-2 transition-all ${
                activeTab === "rag"
                  ? "bg-background text-foreground shadow-xs border border-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Library className="h-4 w-4 text-primary" />
              <span>1. Grounded RAG Citation</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("diagnostic")}
              className={`flex-1 py-3 px-4 rounded-xl text-xs md:text-sm font-semibold flex items-center justify-center gap-2 transition-all ${
                activeTab === "diagnostic"
                  ? "bg-background text-foreground shadow-xs border border-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <ShieldCheck className="h-4 w-4 text-secondary" />
              <span>2. Misconception Check</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("teacher")}
              className={`flex-1 py-3 px-4 rounded-xl text-xs md:text-sm font-semibold flex items-center justify-center gap-2 transition-all ${
                activeTab === "teacher"
                  ? "bg-background text-foreground shadow-xs border border-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <School className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              <span>3. Teacher Intervention</span>
            </button>
          </div>

          {/* Interactive Demo Content Box */}
          <div className="max-w-4xl mx-auto">
            <AnimatePresence mode="wait">
              {activeTab === "rag" && (
                <motion.div
                  key="rag"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -16 }}
                  transition={{ duration: 0.35 }}
                  className="rounded-3xl border border-border bg-background p-6 md:p-8 space-y-6 shadow-xs"
                >
                  <div className="flex items-center justify-between flex-wrap gap-2 border-b border-border pb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="h-9 w-9 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center text-primary">
                        <Brain className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase">Doubt Asked</p>
                        <p className="text-sm font-bold">&quot;Why does a bulb not glow when the switch is open?&quot;</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="border-primary text-primary font-semibold text-xs">
                      Class 8 Science · Open Circuit
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    <p className="text-sm leading-relaxed text-foreground">
                      An open circuit has a break or gap in the conducting path. Electric current requires a continuous closed loop from the battery back to the battery. When the switch is open, the path is broken, so electrons cannot flow.
                    </p>

                    {/* Textbook Citation Block */}
                    <div className="rounded-xl border border-border bg-muted/30 p-4 font-mono text-xs space-y-1.5">
                      <div className="flex items-center gap-2 text-primary font-bold uppercase tracking-wider">
                        <Library className="h-3.5 w-3.5" />
                        <span>Verified Textbook Citation</span>
                      </div>
                      <div className="flex flex-wrap items-baseline gap-2 text-foreground">
                        <span className="font-semibold">NCERT Class 8 Science</span>
                        <span>—</span>
                        <span>Chapter 14: Chemical Effects of Electric Current</span>
                        <span>·</span>
                        <span>pp. 172-174</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === "diagnostic" && (
                <motion.div
                  key="diagnostic"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -16 }}
                  transition={{ duration: 0.35 }}
                  className="rounded-3xl border border-border bg-background p-6 md:p-8 space-y-6 shadow-xs"
                >
                  <div className="flex items-center justify-between flex-wrap gap-2 border-b border-border pb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="h-9 w-9 rounded-xl bg-secondary/15 border border-secondary/30 flex items-center justify-center text-secondary">
                        <ShieldCheck className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase">Diagnostic Misconception Detection</p>
                        <p className="text-sm font-bold">Student Selected: &quot;The battery stops producing electricity when open&quot;</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="border-secondary text-secondary font-semibold text-xs">
                      Misconception Flagged
                    </Badge>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-900 font-medium text-sm leading-relaxed">
                      <strong>AI Diagnosis:</strong> The battery continues to hold electrical potential. The gap at the switch is the only broken link in the circuit, not the battery power source!
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-xl bg-muted border border-border text-xs">
                      <span className="font-semibold">Adaptive Practice Update:</span>
                      <span className="font-bold text-primary">Mastery Score: 42% → 56% (+14%)</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === "teacher" && (
                <motion.div
                  key="teacher"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -16 }}
                  transition={{ duration: 0.35 }}
                  className="rounded-3xl border border-border bg-background p-6 md:p-8 space-y-6 shadow-xs"
                >
                  <div className="flex items-center justify-between flex-wrap gap-2 border-b border-border pb-4">
                    <div className="flex items-center gap-2.5">
                      <div className="h-9 w-9 rounded-xl bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-600">
                        <AlertTriangle className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase">Teacher Dashboard Alert</p>
                        <p className="text-sm font-bold">Student Ankita Bora (High Risk - Open Circuit Pattern)</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="border-red-500 text-red-600 font-semibold text-xs">
                      Intervention Required
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    <div className="p-4 rounded-xl border border-primary/30 bg-primary/10 text-sm leading-relaxed">
                      <div className="flex items-center gap-2 text-primary font-bold text-xs uppercase tracking-wider mb-1">
                        <Lightbulb className="h-4 w-4" />
                        <span>Recommended Classroom Intervention</span>
                      </div>
                      Use a visual circuit diagram showing continuous battery potential with the switch highlighted as the broken link. Follow with 3 open/closed circuit questions.
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </section>

      {/* Dual Role Portals */}
      <section className="px-6 py-20 max-w-6xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-bold tracking-tight">
            {lang === "en" ? "Tailored Portals for Every Role" : "প্ৰতিটো ভূমিকাৰ বাবে পৃথক প'ৰ্টেল"}
          </h2>
          <p className="text-muted-foreground text-sm">
            {lang === "en"
              ? "Empowering students with AI tutoring and teachers with actionable classroom intelligence."
              : "ছাত্ৰ-ছাত্ৰীক AI শিক্ষকতা আৰু শিক্ষকসকলক বাস্তৱসন্মত তথ্য প্ৰদান।"}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Student Portal Card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="p-8 rounded-3xl border border-border bg-card space-y-6 flex flex-col justify-between shadow-xs hover:border-primary transition-all"
          >
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/15 text-foreground font-semibold text-xs border border-primary/30">
                <GraduationCap className="h-4 w-4 text-primary" />
                <span>{lang === "en" ? "Student Learning Portal" : "ছাত্ৰ-ছাত্ৰী প'ৰ্টেল"}</span>
              </div>
              <h3 className="text-2xl font-bold">
                {lang === "en" ? "Ask Doubts & Track Personal Progress" : "সন্দেহ সোধক আৰু অগ্ৰগতি পৰীক্ষা কৰক"}
              </h3>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Multilingual support in English & Assamese (অসমীয়া)</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Verified citations with Class 8 Science textbook chapters</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>3-stage adaptive diagnostic & practice checks</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <span>Concept mastery breakdown dashboard</span>
                </li>
              </ul>
            </div>

            <Button nativeButton={false} render={<Link href="/student/dashboard" />} className="w-full h-11 bg-primary text-primary-foreground hover:bg-primary/90 font-semibold text-sm justify-between">
              <span>{lang === "en" ? "Open Student Dashboard" : "ছাত্ৰ ড্যাশব’ৰ্ড খোলক"}</span>
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </motion.div>

          {/* Teacher Portal Card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="p-8 rounded-3xl border border-border bg-card space-y-6 flex flex-col justify-between shadow-xs hover:border-secondary transition-all"
          >
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/15 text-foreground font-semibold text-xs border border-secondary/30">
                <School className="h-4 w-4 text-secondary" />
                <span>{lang === "en" ? "Teacher Intelligence Hub" : "শিক্ষক ইন্টেলিজেন্স হাব"}</span>
              </div>
              <h3 className="text-2xl font-bold">
                {lang === "en" ? "At-Risk Alerts & Targeted Interventions" : "সতৰ্কতা আৰু নিৰ্দিষ্ট সমাধান"}
              </h3>
              <ul className="space-y-3 text-sm text-muted-foreground">
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-secondary mt-0.5 flex-shrink-0" />
                  <span>Class-wide misconception pattern identification</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-secondary mt-0.5 flex-shrink-0" />
                  <span>Actionable classroom intervention recommendations</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-secondary mt-0.5 flex-shrink-0" />
                  <span>High/Medium risk student flagging & root cause analysis</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-secondary mt-0.5 flex-shrink-0" />
                  <span>Peer-tutoring student recommendation matching</span>
                </li>
              </ul>
            </div>

            <Button nativeButton={false} render={<Link href="/teacher/dashboard" />} className="w-full h-11 bg-secondary text-secondary-foreground hover:bg-secondary/90 font-semibold text-sm justify-between">
              <span>{lang === "en" ? "Open Teacher Dashboard" : "শিক্ষক ড্যাশব’ৰ্ড খোলক"}</span>
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Workflow Timeline */}
      <section className="px-6 py-16 bg-card border-t border-border">
        <div className="max-w-5xl mx-auto space-y-10">
          <div className="text-center space-y-3">
            <Badge variant="outline" className="border-primary text-primary text-xs font-semibold px-3 py-0.5">
              System Workflow
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight">
              {lang === "en" ? "End-to-End Learning Engine Loop" : "এণ্ড-টু-এণ্ড শিকাৰ লুপ"}
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-border bg-background space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-primary">Step 1–3</div>
              <h4 className="font-semibold text-sm">Ask & Detect</h4>
              <p className="text-xs text-muted-foreground">Student submits doubt → Gemini detects Science concept & level.</p>
            </div>

            <div className="p-4 rounded-xl border border-border bg-background space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-primary">Step 4–7</div>
              <h4 className="font-semibold text-sm">RAG & Citation</h4>
              <p className="text-xs text-muted-foreground">Retrieves textbook evidence → Outputs grounded answer with page citation.</p>
            </div>

            <div className="p-4 rounded-xl border border-border bg-background space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-primary">Step 8–11</div>
              <h4 className="font-semibold text-sm">Diagnostic Check</h4>
              <p className="text-xs text-muted-foreground">Detects misconception pattern → Generates 3 adaptive practice questions.</p>
            </div>

            <div className="p-4 rounded-xl border border-border bg-background space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-primary">Step 12–14</div>
              <h4 className="font-semibold text-sm">Mastery & Alert</h4>
              <p className="text-xs text-muted-foreground">Updates score (0–100%) → Flags teacher dashboard with intervention plan.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-background py-8 px-6 text-center text-xs text-muted-foreground">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 font-semibold text-foreground">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>ShikshaSetu AI</span>
          </div>
          <p>© 2026 ShikshaSetu AI. Class 8 Science Multilingual AI Companion.</p>
        </div>
      </footer>
    </div>
  );
}
