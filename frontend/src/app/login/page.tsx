"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, UserCheck, GraduationCap, School, Lock, Mail, Phone, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/auth";
import { login } from "@/lib/api/auth";

type Role = "student" | "teacher";
type Lang = "en" | "as";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>("student");
  const [lang] = useState<Lang>("en");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const setAuth = useAuthStore(state => state.setAuth);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg("");
    
    try {
      const res = await login({
        email: identifier,
        password: password,
        role: role
      });
      setAuth(res);
      if (role === "student") {
        router.push("/student/dashboard");
      } else {
        router.push("/teacher/dashboard");
      }
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Invalid credentials");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-background font-sans text-foreground flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-border bg-background sticky top-0 z-20 w-full">
        <div className="w-full px-6 py-3 flex items-center justify-between gap-3">
          <Link
            href="/"
            className="font-semibold text-sm tracking-tight text-foreground flex items-center gap-1.5 hover:opacity-80 transition-opacity"
          >
            <Sparkles className="h-4 w-4 text-primary" />
            <span>ShikshaSetu AI</span>
          </Link>
          <div className="flex items-center gap-2">

          </div>
        </div>
      </header>

      {/* Main Centered Login Content */}
      <main className="flex-1 flex items-center justify-center p-5 pb-16">
        <div className="w-full max-w-md space-y-6">
          {/* Header text */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full border border-border bg-muted text-muted-foreground text-xs font-medium mb-1">
              <UserCheck className="h-3.5 w-3.5" />
              {lang === "en" ? "Welcome Back" : "পুনৰ স্বাগতম"}
            </div>
            <h1 className="text-3xl font-bold tracking-tight">
              {lang === "en" ? "Sign in to ShikshaSetu" : "শিক্ষা সেতুৰ একাউন্টত প্ৰৱেশ কৰক"}
            </h1>
            <p className="text-sm text-muted-foreground">
              {lang === "en"
                ? "Access your personalized learning journey & mastery tracker"
                : "আপোনাৰ ব্যক্তিগত শিক্ষাদান আৰু দক্ষতা ট্রকাৰত প্ৰৱেশ কৰক"}
            </p>
          </div>

          {/* Role selector tab */}
          <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-muted border border-border">
            <button
              type="button"
              onClick={() => setRole("student")}
              className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all ${
                role === "student"
                  ? "bg-background text-foreground shadow-xs border border-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <GraduationCap className="h-4 w-4 text-primary" />
              {lang === "en" ? "Student" : "ছাত্ৰ-ছাত্ৰী"}
            </button>

            <button
              type="button"
              onClick={() => setRole("teacher")}
              className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all ${
                role === "teacher"
                  ? "bg-background text-foreground shadow-xs border border-border"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <School className="h-4 w-4 text-secondary" />
              {lang === "en" ? "Teacher" : "শিক্ষক-শিক্ষয়িত্ৰী"}
            </button>
          </div>

          {/* Card Container */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-5">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-foreground uppercase tracking-wider mb-1.5">
                  {role === "student"
                    ? lang === "en"
                      ? "Student Roll No or Mobile"
                      : "ৰোল নম্বৰ বা মোবাইল নম্বৰ"
                    : lang === "en"
                      ? "Teacher Email or ID"
                      : "ইমেইল বা শিক্ষক আইডি"}
                </label>
                <div className="relative">
                  {role === "student" ? (
                    <Phone className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  )}
                  <input
                    type="text"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder={
                      role === "student"
                        ? lang === "en"
                          ? "e.g. 9876543210 or Roll #8"
                          : "উদা. ৯৮৭৬৫ND৩২১০ বা ৰোল #৮"
                        : "teacher@school.gov.in"
                    }
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-input bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-semibold text-foreground uppercase tracking-wider">
                    {lang === "en" ? "Password / PIN" : "পাছৱৰ্ড / পিন"}
                  </label>
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      alert(lang === "en" ? "Password reset instructions sent." : "পাছৱৰ্ড পুনৰুদ্ধাৰ নিৰ্দেশনা প্ৰেৰণ কৰা হৈছে।");
                    }}
                    className="text-xs text-muted-foreground hover:text-primary transition-colors"
                  >
                    {lang === "en" ? "Forgot PIN?" : "পিন পাহৰিলে?"}
                  </a>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-input bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
              </div>

              {errorMsg && (
                <div className="flex items-center gap-2 text-destructive text-sm font-medium mt-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-semibold text-sm h-11 flex items-center justify-center gap-2 transition-all mt-2"
              >
                {isSubmitting ? (
                  <span>{lang === "en" ? "Signing in…" : "প্ৰৱেশ কৰা হৈছে…"}</span>
                ) : (
                  <>
                    <span>{lang === "en" ? "Sign In" : "প্ৰৱেশ কৰক"}</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </form>

            <div className="relative flex items-center justify-center my-2">
              <div className="border-t border-border w-full" />
              <span className="bg-card px-3 text-[11px] font-medium text-muted-foreground uppercase tracking-wider absolute">
                {lang === "en" ? "or" : "বা"}
              </span>
            </div>

            {/* Quick Guest Access Link */}
            <Link
              href="/ask"
              className="w-full py-2.5 rounded-xl border border-border bg-muted/40 hover:bg-muted text-foreground text-sm font-medium flex items-center justify-center gap-2 transition-colors"
            >
              <Sparkles className="h-4 w-4 text-primary" />
              <span>{lang === "en" ? "Continue as Guest" : "অতিথি হিচাপে অব্যাহত ৰাখক"}</span>
            </Link>
          </div>

          {/* Footer note */}
          <p className="text-center text-xs text-muted-foreground">
            {lang === "en"
              ? "Don't have an account? Contact your school administrator."
              : "একাউন্ট নাই? আপোনাৰ বিদ্যালয় প্ৰশাসনৰ সৈতে যোগাযোগ কৰক।"}
          </p>
        </div>
      </main>
    </div>
  );
}
