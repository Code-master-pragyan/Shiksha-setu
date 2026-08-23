import { ChevronRight, CheckCircle2, XCircle } from "lucide-react";
import { getMasteryTier } from "@/lib/formatters";
import { cn } from "@/lib/utils";

// ─────────────────────────────────────────────────────────────────────────────
// MASTERY BAR  (clean static progress indicator)
// ─────────────────────────────────────────────────────────────────────────────

export function MasteryBar({
  fromScore,
  toScore,
}: {
  fromScore: number;
  toScore: number;
}) {
  const tier = getMasteryTier(toScore);
  const fromPct = Math.round(fromScore * 100);
  const toPct = Math.round(toScore * 100);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Mastery
        </span>
        <div className="flex items-baseline gap-1.5">
          <span className="text-sm text-muted-foreground line-through tabular-nums">
            {fromPct}%
          </span>
          <ChevronRight className="h-3 w-3 text-muted-foreground/50" />
          <span
            className="text-3xl font-bold tabular-nums leading-none"
            style={{ color: tier?.color ?? "#4d9de0" }}
          >
            {toPct}
            <span className="text-xl">%</span>
          </span>
        </div>
      </div>

      {/* Track */}
      <div className="relative h-2.5 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${toPct}%`,
            backgroundColor: tier?.color ?? "#4d9de0",
          }}
        />
      </div>

      {/* Tier label */}
      {tier && (
        <div className="flex items-center gap-2">
          <div
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: tier.color }}
          />
          <span
            className="text-sm font-semibold"
            style={{ color: tier.color }}
          >
            {tier.label}
          </span>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// MCQ OPTION
// ─────────────────────────────────────────────────────────────────────────────

export function McqOption({
  id,
  label,
  selected,
  submitted,
  isCorrect,
  onClick,
}: {
  id: string;
  label: string;
  selected: boolean;
  submitted: boolean;
  isCorrect: boolean;
  onClick: () => void;
}) {
  return (
    <button
      disabled={submitted}
      onClick={onClick}
      className={cn(
        "w-full text-left px-4 py-3 rounded-lg border text-sm transition-colors focus-visible:outline-none",
        !submitted && selected && "border-primary bg-primary/10 text-foreground font-medium",
        !submitted && !selected && "border-border bg-card hover:bg-muted/50 text-foreground/90",
        submitted && isCorrect && "border-emerald-500 bg-emerald-500/10 text-emerald-800 font-medium",
        submitted && selected && !isCorrect && "border-red-500 bg-red-500/10 text-red-800 font-medium",
        submitted && !selected && !isCorrect && "border-border/40 bg-transparent opacity-40 cursor-default"
      )}
    >
      <div className="flex items-center gap-3">
        <span
          className={cn(
            "flex-shrink-0 h-5 w-5 rounded-full border text-[10px] font-bold flex items-center justify-center",
            !submitted && selected
              ? "border-primary text-primary"
              : "border-border text-muted-foreground",
            submitted && isCorrect ? "border-emerald-500 text-emerald-500" : "",
            submitted && selected && !isCorrect ? "border-red-500 text-red-500" : ""
          )}
        >
          {id.toUpperCase()}
        </span>
        <span className="flex-1">{label}</span>
        {submitted && isCorrect && (
          <CheckCircle2 className="flex-shrink-0 h-4 w-4 text-emerald-500" />
        )}
        {submitted && selected && !isCorrect && (
          <XCircle className="flex-shrink-0 h-4 w-4 text-red-500" />
        )}
      </div>
    </button>
  );
}
