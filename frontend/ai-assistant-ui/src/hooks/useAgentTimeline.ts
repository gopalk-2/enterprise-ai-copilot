// src/hooks/useAgentTimeline.ts
// Collects streaming status/cache events into a typed, timestamped timeline.

import { useState, useCallback, useRef } from "react";

export type StepStatus = "pending" | "active" | "done" | "error" | "cached";

export interface TimelineStep {
  id: string;
  label: string;
  icon: string;        // emoji icon
  status: StepStatus;
  startedAt: number;   // Date.now() when added
  elapsedMs?: number;  // set when completed
}

function iconForLabel(label: string): string {
  const l = label.toLowerCase();
  if (l.includes("cache") && l.includes("hit")) return "⚡";
  if (l.includes("cache") && l.includes("miss")) return "🔍";
  if (l.includes("semantic cache")) return "⚡";
  if (l.includes("retrieval") || l.includes("searching") || l.includes("knowledge base")) return "📚";
  if (l.includes("agent") || l.includes("specialist") || l.includes("delegat")) return "🤖";
  if (l.includes("classif") || l.includes("routing") || l.includes("classified")) return "🧭";
  if (l.includes("error")) return "⚠️";
  if (l.includes("complete") || l.includes("done") || l.includes("resolved") || l.includes("generat")) return "✅";
  if (l.includes("data") || l.includes("analyz")) return "📊";
  if (l.includes("code") || l.includes("review")) return "💻";
  if (l.includes("support")) return "🎧";
  if (l.includes("greet")) return "👋";
  return "⚙️";
}

function statusForLabel(label: string): StepStatus {
  const l = label.toLowerCase();
  if (l.includes("⚡") || (l.includes("cache") && l.includes("hit"))) return "cached";
  if (l.includes("error")) return "error";
  return "active";
}

export function useAgentTimeline() {
  const [steps, setSteps] = useState<TimelineStep[]>([]);
  const stepTimers = useRef<Record<string, number>>({});

  const addStep = useCallback((label: string) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const now = Date.now();
    stepTimers.current[id] = now;

    const newStep: TimelineStep = {
      id,
      label,
      icon: iconForLabel(label),
      status: statusForLabel(label),
      startedAt: now,
    };

    setSteps((prev) => {
      // Mark the previous active step as done
      const updated = prev.map((s) =>
        s.status === "active"
          ? { ...s, status: "done" as StepStatus, elapsedMs: now - s.startedAt }
          : s
      );
      return [...updated, newStep];
    });

    return id;
  }, []);

  const completeAll = useCallback(() => {
    const now = Date.now();
    setSteps((prev) =>
      prev.map((s) =>
        s.status === "active" || s.status === "cached"
          ? { ...s, status: "done" as StepStatus, elapsedMs: now - s.startedAt }
          : s
      )
    );
  }, []);

  const resetTimeline = useCallback(() => {
    setSteps([]);
    stepTimers.current = {};
  }, []);

  return { steps, addStep, completeAll, resetTimeline };
}
