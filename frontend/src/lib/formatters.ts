/**
 * Static UI formatters and text for ShikshaSetu AI
 */

export interface BilingualText {
  en: string;
  as: string;
}

export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface MasteryTier {
  min: number;
  max: number;
  label: string;
  color: string;
}

export const MASTERY_TIERS: MasteryTier[] = [
  { min: 0, max: 0.4, label: "Beginner", color: "#ef4444" },
  { min: 0.4, max: 0.7, label: "Intermediate", color: "#f59e0b" },
  { min: 0.7, max: 1.0, label: "Advanced", color: "#10b981" }
];

export function getMasteryTier(score: number): MasteryTier | undefined {
  return MASTERY_TIERS.find(
    (t) => score >= t.min && (score < t.max || t.max === 1.0)
  );
}

const NO_MATCH_FALLBACK: BilingualText = {
  en: "I'm sorry, I couldn't find a direct answer in your textbooks for that specific question. Try rephrasing or asking about a specific concept like cells or circuits.",
  as: "ক্ষমা কৰিব, মই আপোনাৰ পাঠ্যপুথিত সেই নিৰ্দিষ্ট প্ৰশ্নৰ পোনে পোনে উত্তৰ বিচাৰি নাপালোঁ। অনুগ্ৰহ কৰি বেলেগ ধৰণে সুধি চাওক।"
};

export function getNoMatchFallback(): BilingualText {
  return NO_MATCH_FALLBACK;
}
