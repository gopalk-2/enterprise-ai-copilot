"use client";

import React, { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Artifact } from "./ArtifactPanel";

// Language → display label
const LANG_LABELS: Record<string, string> = {
  python: "Python", typescript: "TypeScript", javascript: "JavaScript",
  bash: "Shell", sql: "SQL", json: "JSON", yaml: "YAML", go: "Go",
};

// ── Code renderer ─────────────────────────────────────────────────────────────
function CodeArtifact({ content, language }: { content: string; language?: string }) {
  const label = language ? (LANG_LABELS[language.toLowerCase()] ?? language) : "Code";
  return (
    <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-900 shadow-inner">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{label}</span>
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
        </div>
      </div>
      <pre className="overflow-x-auto p-5 text-xs leading-relaxed text-slate-200 font-mono whitespace-pre">
        {content}
      </pre>
    </div>
  );
}

// ── Markdown renderer ─────────────────────────────────────────────────────────
function MarkdownArtifact({ content }: { content: string }) {
  return (
    <div className="prose prose-sm max-w-none
      prose-headings:text-slate-800 prose-headings:font-bold
      prose-h1:text-xl prose-h2:text-lg prose-h3:text-base
      prose-p:text-slate-600 prose-p:leading-relaxed
      prose-li:text-slate-600 prose-li:my-0.5
      prose-strong:text-slate-800
      prose-code:bg-slate-100 prose-code:text-indigo-700 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:font-mono
      prose-a:text-indigo-600 prose-a:underline
      prose-blockquote:border-l-4 prose-blockquote:border-indigo-300 prose-blockquote:pl-4 prose-blockquote:text-slate-500
      prose-hr:border-slate-200
      prose-table:text-sm prose-th:bg-slate-50 prose-th:px-3 prose-th:py-2 prose-td:px-3 prose-td:py-2"
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}

// ── Mermaid renderer ──────────────────────────────────────────────────────────
function MermaidArtifact({ content }: { content: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const id = useRef(`mermaid-${Math.random().toString(36).slice(2, 9)}`);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({ startOnLoad: false, theme: "default", securityLevel: "loose" });
        const { svg } = await mermaid.render(id.current, content);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = `<pre class="text-xs text-red-500 p-4">${String(err)}</pre>`;
        }
      }
    })();
    return () => { cancelled = true; };
  }, [content]);

  return (
    <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm overflow-x-auto">
      <div ref={containerRef} className="flex items-center justify-center min-h-[120px]">
        <span className="text-xs text-slate-400 animate-pulse">Rendering diagram…</span>
      </div>
    </div>
  );
}

// ── Public renderer ───────────────────────────────────────────────────────────
export default function ArtifactRenderer({ artifact }: { artifact: Artifact }) {
  switch (artifact.artifact_type) {
    case "code":
      return <CodeArtifact content={artifact.content} language={artifact.language} />;
    case "mermaid":
      return <MermaidArtifact content={artifact.content} />;
    case "markdown":
    default:
      return <MarkdownArtifact content={artifact.content} />;
  }
}
