"use client";

import React, { useState } from "react";
import ArtifactRenderer from "./ArtifactRenderer";

export interface Artifact {
  artifact_type: "markdown" | "code" | "mermaid";
  title: string;
  content: string;
  language?: string; // for code artifacts e.g. "python", "typescript"
}

interface ArtifactPanelProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export default function ArtifactPanel({ artifact, onClose }: ArtifactPanelProps) {
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === "code"
      ? (artifact.language === "python" ? ".py" : artifact.language === "typescript" ? ".ts" : ".txt")
      : artifact.artifact_type === "mermaid" ? ".mmd" : ".md";
    const blob = new Blob([artifact.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${artifact.title.replace(/\s+/g, "_")}${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const typeBadge: Record<string, { label: string; color: string }> = {
    markdown: { label: "Document", color: "bg-indigo-100 text-indigo-700 border-indigo-200" },
    code: { label: "Code", color: "bg-emerald-100 text-emerald-700 border-emerald-200" },
    mermaid: { label: "Diagram", color: "bg-purple-100 text-purple-700 border-purple-200" },
  };

  const badge = typeBadge[artifact.artifact_type] ?? typeBadge.markdown;

  return (
    <div className="artifact-panel flex flex-col w-[440px] min-w-[320px] max-w-[480px] h-full border-l border-slate-200 bg-white shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-slate-900 flex-shrink-0">
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-base">
              {artifact.artifact_type === "code" ? "💻" : artifact.artifact_type === "mermaid" ? "📐" : "📄"}
            </span>
            <span className="font-semibold text-white text-sm truncate max-w-[260px]">
              {artifact.title}
            </span>
          </div>
          <span className={`self-start text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full border ${badge.color}`}>
            {badge.label}
          </span>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            onClick={handleCopy}
            title="Copy content"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-700 transition-all"
          >
            {copied ? (
              <>
                <svg className="w-3.5 h-3.5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            title="Download"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-700 transition-all"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Save
          </button>

          <button
            onClick={onClose}
            title="Close panel"
            className="ml-1 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        <ArtifactRenderer artifact={artifact} />
      </div>
    </div>
  );
}
