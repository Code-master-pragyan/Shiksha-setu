"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Sparkles, User, Brain, BookOpen, BarChart3, HelpCircle, Library } from "lucide-react";
import { useAuthStore } from "@/lib/store/auth";

type Lang = "en" | "as";

export default function StudentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [lang] = useState<Lang>("en");
  
  const token = useAuthStore(state => state.token);
  const user = useAuthStore(state => state.user);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    if (!token || user?.role !== "student") {
      router.replace("/login");
    }
  }, [mounted, token, user, router]);

  if (!mounted || !token || user?.role !== "student") {
    return null;
  }

  const navLinks = [
    { href: "/student/dashboard", label: lang === "en" ? "Dashboard" : "ড্যাশব’ৰ্ড", icon: BarChart3 },
    { href: "/ask", label: lang === "en" ? "Ask Doubt" : "সন্দেহ সোধক", icon: HelpCircle },
    { href: "/student/practice", label: lang === "en" ? "Practice" : "অনুশীলন", icon: BookOpen },
    { href: "/student/progress", label: lang === "en" ? "Progress" : "অগ্ৰগতি", icon: Brain },
    { href: "/student/library", label: lang === "en" ? "Library" : "পুথিভঁৰাল", icon: Library },
  ];

  return (
    <div className="min-h-screen bg-background font-sans text-foreground flex flex-col">
      {/* Navbar */}
      <header className="border-b border-border bg-background sticky top-0 z-30 w-full">
        <div className="w-full px-6 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-6">
            <Link
              href="/"
              className="font-semibold text-sm tracking-tight text-foreground flex items-center gap-1.5 hover:opacity-80 transition-opacity"
            >
              <Sparkles className="h-4 w-4 text-primary" />
              <span>ShikshaSetu AI</span>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const active = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                      active
                        ? "bg-primary/20 text-foreground border border-primary/40"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    <span>{link.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-3">


            <Link
              href="/student/profile"
              aria-label="Profile"
              className="h-8.5 w-8.5 rounded-full border border-border bg-muted flex items-center justify-center text-foreground hover:bg-primary/20 hover:border-primary transition-colors"
            >
              <User className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content Shell */}
      <div className="flex-1">{children}</div>
    </div>
  );
}
