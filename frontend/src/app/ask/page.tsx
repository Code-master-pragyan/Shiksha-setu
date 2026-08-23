import { DoubtFlow } from "@/components/shared/DoubtFlow";

export const metadata = {
  title: "Ask a Doubt — ShikshaSetu AI",
  description: "Get AI-powered answers to your Science doubts with source citations and mastery tracking.",
};

export default function AskPage() {
  return (
    <DoubtFlow
      mode="student"
      initialMasteryScore={0}
    />
  );
}
