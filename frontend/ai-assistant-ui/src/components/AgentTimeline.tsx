"use client";

import React, { useState } from "react";
import { TimelineStep, StepStatus } from "@/hooks/useAgentTimeline";

interface AgentTimelineProps {
  steps: TimelineStep[];
  isComplete: boolean;
}

function StatusIndicator({ status }: { status: StepStatus }) {
  if (status === "done") {
    return (
      <span className="w-4 h-4 flex items-center justify-center rounded-full bg-emerald-500/12 flex-shrink-0">
        <svg className="w-2.5 h-2.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      </span>
    );
  }
  if (status === "cached") {
    return <span className="w-4 h-4 flex-shrink-0 flex items-center justify-center text-[11px]">⚡</span>;
  }
  if (status === "error") {
    return (
      <span className="w-4 h-4 flex-shrink-0 flex items-center justify-center rounded-full bg-red-500/10">
        <svg className="w-2.5 h-2.5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </span>
    );
  }
  // active
  return (
    <span className="w-4 h-4 flex-shrink-0 flex items-center justify-center">
      <span className="w-2.5 h-2.5 rounded-full border-[1.5px] border-zinc-400 border-t-transparent animate-spin" />
    </span>
  );
}

function elapsed(ms?: number) {
  if (!ms || ms < 20) return "";
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;
}

export default function AgentTimeline({ steps, isComplete }: AgentTimelineProps) {
  const [expanded, setExpanded] = useState(true);
  if (steps.length === 0) return null;

  return (
    <div className="mb-4">
      {/* Header toggle */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-1.5 mb-2 group"
      >
        <svg
          className={`w-3 h-3 text-zinc-400 transition-transform duration-150 ${expanded ? "" : "-rotate-90"}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        <span className="text-[11px] text-zinc-400 font-medium group-hover:text-zinc-600 transition-colors">
          {isComplete ? "Completed" : "Working…"}
        </span>
        <span className="text-[10px] text-zinc-300 bg-zinc-100 px-1.5 py-0.5 rounded-full font-medium">
          {steps.length} steps
        </span>
      </button>

      {/* Steps */}
      {expanded && (
        <div className="relative pl-5 space-y-1">
          {/* Vertical track */}
          <div className="absolute left-2 top-1 bottom-1 w-px bg-zinc-100" />

          {steps.map((step, i) => (
            <div
              key={step.id}
              className="timeline-step relative flex items-center gap-2 py-0.5 group"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              {/* Track dot */}
              <span className="absolute -left-3.5 w-1.5 h-1.5 rounded-full bg-zinc-200 group-hover:bg-zinc-400 transition-colors flex-shrink-0" />

              <StatusIndicator status={step.status} />

              <span className={`text-[12px] leading-tight font-medium flex-1 min-w-0 truncate transition-colors ${
                step.status === "active" ? "text-zinc-700" :
                step.status === "done" ? "text-zinc-500" :
                step.status === "cached" ? "text-amber-600" :
                step.status === "error" ? "text-red-500" : "text-zinc-400"
              }`}>
                {step.icon} {step.label}
              </span>

              {step.elapsedMs !== undefined && step.elapsedMs > 0 && (
                <span className="text-[10px] text-zinc-300 flex-shrink-0 font-mono tabular-nums">
                  {elapsed(step.elapsedMs)}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
