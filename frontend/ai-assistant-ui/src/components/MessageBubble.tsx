"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import SourcesPanel from "./SourcesPanel";
import DynamicRenderer from "./DynamicRenderer";
import AgentTimeline from "./AgentTimeline";
import { TimelineStep } from "@/hooks/useAgentTimeline";
import { Artifact } from "./ArtifactPanel";
import { useState } from "react";

interface UIComponent {
  component: string;
  data: any;
}

interface MessageBubbleProps {
  text: string;
  isUser: boolean;
  time?: string;
  sources?: any[];
  uiComponents?: UIComponent[];
  timelineSteps?: TimelineStep[];
  artifact?: Artifact | null;
  cacheHit?: boolean;
  isStreaming?: boolean;
  onOpenArtifact?: (artifact: Artifact) => void;
}

// ── Copy button for code blocks ───────────────────────────────────────────────
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handle = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={handle}
      className="absolute top-3 right-3 flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white text-[11px] font-medium transition-all"
    >
      {copied ? (
        <>
          <svg className="w-3 h-3 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          <span className="text-emerald-400">Copied</span>
        </>
      ) : (
        <>
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Copy
        </>
      )}
    </button>
  );
}

// ── Custom code block renderer ────────────────────────────────────────────────
function CodeBlock({ language, children }: { language: string; children: string }) {
  return (
    <div className="relative my-4 rounded-xl overflow-hidden border border-[#2d2d2d] shadow-lg">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#1e1e1e] border-b border-[#2d2d2d]">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
        </div>
        <span className="text-[11px] text-slate-500 font-mono uppercase tracking-wider">
          {language || "code"}
        </span>
      </div>
      {/* Highlighted code */}
      <div className="relative">
        <SyntaxHighlighter
          language={language || "text"}
          style={oneDark}
          customStyle={{
            margin: 0,
            padding: "1.25rem 1.25rem 1.25rem 1rem",
            background: "#1a1a1a",
            fontSize: "0.8rem",
            lineHeight: "1.7",
            borderRadius: 0,
          }}
          showLineNumbers
          lineNumberStyle={{ color: "#4a4a4a", minWidth: "2.5em", paddingRight: "1.25em", userSelect: "none" }}
        >
          {children}
        </SyntaxHighlighter>
        <CopyButton text={children} />
      </div>
    </div>
  );
}

// ── Inline code ───────────────────────────────────────────────────────────────
function InlineCode({ children }: { children: React.ReactNode }) {
  return (
    <code className="px-1.5 py-0.5 rounded-md bg-slate-100 text-violet-700 text-[0.8em] font-mono border border-slate-200/80">
      {children}
    </code>
  );
}

export default function MessageBubble({
  text, isUser, time, sources, uiComponents,
  timelineSteps, artifact, cacheHit, isStreaming, onOpenArtifact,
}: MessageBubbleProps) {
  const hasTimeline = !isUser && timelineSteps && timelineSteps.length > 0;

  return (
    <div className={`msg-animate flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex gap-3 ${isUser ? "flex-row-reverse max-w-[80%]" : "flex-row max-w-full w-full"}`}>

        {/* Avatar */}
        <div className="flex-shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-7 h-7 rounded-full bg-zinc-900 flex items-center justify-center text-white text-[11px] font-semibold shadow-sm">
              U
            </div>
          ) : (
            <div className="relative w-7 h-7 rounded-lg bg-zinc-900 flex items-center justify-center shadow-sm flex-shrink-0">
              <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              {cacheHit && (
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 rounded-full flex items-center justify-center text-[7px] shadow-sm border border-white" title="From semantic cache">
                  ⚡
                </span>
              )}
            </div>
          )}
        </div>

        {/* Content column */}
        <div className="flex flex-col min-w-0 flex-1">

          {/* Agent Timeline */}
          {hasTimeline && (
            <AgentTimeline steps={timelineSteps!} isComplete={!isStreaming} />
          )}

          {/* Message content */}
          {isUser ? (
            /* ── User bubble ── */
            <div className="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-zinc-900 text-white text-sm leading-relaxed">
              {text}
            </div>
          ) : (
            /* ── AI message — no bubble, just clean prose ── */
            <div className="min-w-0 w-full">
              {text ? (
                <div className="ai-prose text-[0.925rem] leading-[1.8] text-zinc-800">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // ── Code blocks ──
                      code({ className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        const isBlock = !!match || String(children).includes("\n");
                        if (isBlock) {
                          return (
                            <CodeBlock language={match?.[1] || "text"}>
                              {String(children).replace(/\n$/, "")}
                            </CodeBlock>
                          );
                        }
                        return <InlineCode>{children}</InlineCode>;
                      },
                      // ── Headings ──
                      h1: ({ children }) => <h1 className="text-xl font-bold text-zinc-900 mt-6 mb-3 first:mt-0">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-base font-semibold text-zinc-900 mt-5 mb-2 first:mt-0 pb-1 border-b border-zinc-100">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-sm font-semibold text-zinc-800 mt-4 mb-1.5">{children}</h3>,
                      // ── Paragraphs ──
                      p: ({ children }) => <p className="mb-3 last:mb-0 text-zinc-700 leading-[1.8]">{children}</p>,
                      // ── Lists ──
                      ul: ({ children }) => <ul className="mb-3 space-y-1 pl-5">{children}</ul>,
                      ol: ({ children }) => <ol className="mb-3 space-y-1 pl-5 list-decimal">{children}</ol>,
                      li: ({ children }) => (
                        <li className="text-zinc-700 leading-relaxed relative before:absolute before:-left-4 before:text-zinc-400 before:content-['–'] list-none">
                          {children}
                        </li>
                      ),
                      // ── Blockquote ──
                      blockquote: ({ children }) => (
                        <blockquote className="pl-4 border-l-2 border-zinc-300 text-zinc-500 italic my-3">
                          {children}
                        </blockquote>
                      ),
                      // ── Table ──
                      table: ({ children }) => (
                        <div className="my-4 overflow-x-auto rounded-xl border border-zinc-200 shadow-sm">
                          <table className="w-full text-sm">{children}</table>
                        </div>
                      ),
                      thead: ({ children }) => <thead className="bg-zinc-50 border-b border-zinc-200">{children}</thead>,
                      th: ({ children }) => <th className="px-4 py-2.5 text-left text-xs font-semibold text-zinc-500 uppercase tracking-wider">{children}</th>,
                      td: ({ children }) => <td className="px-4 py-2.5 text-zinc-700 border-t border-zinc-100">{children}</td>,
                      // ── HR ──
                      hr: () => <hr className="my-4 border-zinc-100" />,
                      // ── Links / citations ──
                      a: ({ href, children }) => {
                        if (href === "#source" || (href && !href.startsWith("http") && !href.startsWith("mailto"))) {
                          return (
                            <span
                              onClick={() => alert(`View source: ${String(children)}`)}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-violet-50 text-violet-700 cursor-pointer hover:bg-violet-100 transition-colors border border-violet-200/60"
                            >
                              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              {children}
                            </span>
                          );
                        }
                        return (
                          <a href={href} className="text-violet-600 underline decoration-violet-200 underline-offset-2 hover:decoration-violet-500 transition-colors" target="_blank" rel="noopener noreferrer">
                            {children}
                          </a>
                        );
                      },
                      // ── Strong / em ──
                      strong: ({ children }) => <strong className="font-semibold text-zinc-900">{children}</strong>,
                      em: ({ children }) => <em className="italic text-zinc-600">{children}</em>,
                    }}
                  >
                    {text}
                  </ReactMarkdown>

                  {/* Streaming cursor */}
                  {isStreaming && (
                    <span className="inline-block w-[2px] h-[1.1em] bg-violet-500 ml-0.5 cursor-blink rounded-sm align-middle" />
                  )}
                </div>
              ) : isStreaming ? (
                /* Empty streaming state */
                <div className="flex items-center gap-2 text-zinc-400 text-sm py-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              ) : null}
            </div>
          )}

          {/* Artifact button */}
          {!isUser && artifact && onOpenArtifact && (
            <button
              onClick={() => onOpenArtifact(artifact)}
              className="mt-3 self-start flex items-center gap-2 px-3.5 py-2 rounded-lg bg-zinc-50 border border-zinc-200 text-zinc-700 text-xs font-medium hover:bg-zinc-100 hover:border-zinc-300 transition-all group"
            >
              <span className="text-sm">
                {artifact.artifact_type === "code" ? "💻" : artifact.artifact_type === "mermaid" ? "📐" : "📄"}
              </span>
              <span className="truncate max-w-[240px]">{artifact.title}</span>
              <svg className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-600 group-hover:translate-x-0.5 transition-all ml-auto flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}

          {/* Dynamic UI (charts / tables) */}
          {!isUser && uiComponents && uiComponents.length > 0 && (
            <DynamicRenderer components={uiComponents} />
          )}

          {/* Sources */}
          {!isUser && sources && sources.length > 0 && (
            <SourcesPanel sources={sources} />
          )}

          {/* Timestamp + cache badge */}
          {time && (
            <div className={`flex mt-2 items-center gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
              <span className="text-[10px] text-zinc-400">{time}</span>
              {!isUser && cacheHit && (
                <span className="text-[10px] text-amber-500 font-medium flex items-center gap-0.5">
                  ⚡ instant
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}