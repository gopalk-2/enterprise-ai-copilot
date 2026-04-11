"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect, useRef, useCallback } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import ArtifactPanel, { Artifact } from "./ArtifactPanel";
import { useAgentTimeline, TimelineStep } from "@/hooks/useAgentTimeline";

interface UIComponent {
  component: string;
  data: any;
}

interface Message {
  text: string;
  user: boolean;
  time?: string;
  sources?: any[];
  uiComponents?: UIComponent[];
  timelineSteps?: TimelineStep[];
  artifact?: Artifact | null;
  cacheHit?: boolean;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const { steps, addStep, completeAll, resetTimeline } = useAgentTimeline();
  const stepsRef = useRef<TimelineStep[]>([]);
  useEffect(() => { stepsRef.current = steps; }, [steps]);

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("is_logged_in");
    if (!isLoggedIn) router.push("/login");
  }, [router]);

  // Smooth scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, steps]);

  const sendMessage = useCallback(async (msg: string) => {
    if (!msg.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        text: msg,
        user: true,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setIsLoading(true);
    resetTimeline();

    let assistantMessage = "";
    let collectedSources: any[] = [];
    let collectedUIComponents: UIComponent[] = [];
    let artifactFromStream: Artifact | null = null;
    let cacheHit = false;
    let buffer = "";
    let lastRenderTime = Date.now();

    try {
      const res = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: msg }),
        credentials: "include",
      });

      if (res.status === 401) {
        localStorage.removeItem("is_logged_in");
        router.push("/login");
        return;
      }
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      setMessages((prev) => [
        ...prev,
        { text: "", user: false, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), sources: [], uiComponents: [], timelineSteps: [] },
      ]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            switch (event.type) {
              case "status":
                addStep(event.content);
                setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], timelineSteps: [...stepsRef.current] }; return u; });
                break;
              case "cache_status":
                cacheHit = !!event.hit;
                addStep(event.content);
                setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], timelineSteps: [...stepsRef.current], cacheHit }; return u; });
                break;
              case "token":
                assistantMessage += event.content;
                if (Date.now() - lastRenderTime > 40) {
                  setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], text: assistantMessage }; return u; });
                  lastRenderTime = Date.now();
                }
                break;
              case "sources":
                collectedSources = event.content || [];
                setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], sources: collectedSources }; return u; });
                break;
              case "ui_component":
                collectedUIComponents.push({ component: event.component, data: event.data });
                setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], uiComponents: [...collectedUIComponents] }; return u; });
                break;
              case "artifact":
                artifactFromStream = { artifact_type: event.artifact_type, title: event.title, content: event.content, language: event.language };
                setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], artifact: artifactFromStream }; return u; });
                setActiveArtifact(artifactFromStream);
                break;
              case "done":
                completeAll();
                setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], text: assistantMessage, timelineSteps: [...stepsRef.current] }; return u; });
                break;
            }
          } catch {
            assistantMessage += line;
            if (Date.now() - lastRenderTime > 40) {
              setMessages((prev) => { const u = [...prev]; u[u.length - 1] = { ...u[u.length - 1], text: assistantMessage }; return u; });
              lastRenderTime = Date.now();
            }
          }
        }
      }
    } catch {
      completeAll();
      setMessages((prev) => [...prev, { text: "Connection lost. Please try again.", user: false }]);
    } finally {
      setIsLoading(false);
      setMessages((prev) => {
        const u = [...prev];
        if (u.length > 0 && !u[u.length - 1].user) {
          u[u.length - 1] = { ...u[u.length - 1], text: assistantMessage, timelineSteps: [...stepsRef.current] };
        }
        return u;
      });
    }
  }, [addStep, completeAll, resetTimeline, router]);

  const suggestions = [
    { icon: "📋", title: "Summarize Policy", desc: "Remote work guidelines" },
    { icon: "📊", title: "Analyze Revenue", desc: "Q3 performance metrics" },
    { icon: "🛡️", title: "Check SLA Status", desc: "Severity 1 compliance" },
    { icon: "💻", title: "Review Code", desc: "Tech stack compliance" },
  ];

  const panelOpen = !!activeArtifact;

  return (
    <div className="flex h-full overflow-hidden">
      {/* ── Chat column ─────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#f9f9f8]">

        {/* Mobile header */}
        <header className="md:hidden flex-shrink-0 flex items-center justify-between px-5 py-3.5 bg-white border-b border-zinc-200">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-zinc-900 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            </div>
            <span className="font-semibold text-zinc-900 text-sm">COGNO AI</span>
          </div>
          <button onClick={() => { localStorage.removeItem("is_logged_in"); router.push("/login"); }} className="text-xs text-zinc-400 hover:text-red-500 transition-colors">
            Sign out
          </button>
        </header>

        {/* Messages — flex-1 + overflow-y-auto = correct layout, no absolute footer */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-3xl mx-auto px-4 md:px-8 py-8">

            {messages.length === 0 ? (
              /* ── Empty state ── */
              <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
                <div className="w-12 h-12 rounded-2xl bg-zinc-900 flex items-center justify-center mb-6 shadow-lg">
                  <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-semibold text-zinc-900 mb-2 tracking-tight">How can I help?</h2>
                <p className="text-zinc-500 text-sm max-w-xs leading-relaxed mb-10">
                  Access enterprise data, review code, analyze metrics, or trigger workflows — securely.
                </p>
                <div className="grid grid-cols-2 gap-2 w-full max-w-md">
                  {suggestions.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(`${s.title}: ${s.desc}`)}
                      className="flex items-start gap-3 p-3.5 rounded-xl border border-zinc-200 bg-white hover:border-zinc-300 hover:shadow-sm transition-all text-left group"
                    >
                      <span className="text-lg mt-0.5">{s.icon}</span>
                      <div>
                        <div className="text-sm font-medium text-zinc-800 group-hover:text-zinc-900">{s.title}</div>
                        <div className="text-xs text-zinc-400 mt-0.5">{s.desc}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6 pb-4">
                {messages.map((m, i) => (
                  <MessageBubble
                    key={i}
                    text={m.text}
                    isUser={m.user}
                    time={m.time}
                    sources={m.sources}
                    uiComponents={m.uiComponents}
                    timelineSteps={m.timelineSteps}
                    artifact={m.artifact}
                    cacheHit={m.cacheHit}
                    isStreaming={!m.user && isLoading && i === messages.length - 1}
                    onOpenArtifact={(a) => setActiveArtifact(a)}
                  />
                ))}
                <div ref={bottomRef} />
              </div>
            )}
          </div>
        </div>

        {/* ── Input — normal flow, NOT absolute ────────────────────── */}
        <div className="flex-shrink-0 border-t border-zinc-200 bg-[#f9f9f8] px-4 md:px-8 py-4">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={sendMessage} disabled={isLoading} />
            <p className="text-center text-[10px] text-zinc-400 mt-3 tracking-widest uppercase">
              COGNO AI · Enterprise Secure · Multi-Agent
            </p>
          </div>
        </div>
      </div>

      {/* ── Artifact panel ────────────────────────────────────────── */}
      {panelOpen && (
        <div className="hidden md:flex flex-shrink-0 h-full animate-slide-in-right border-l border-zinc-200">
          <ArtifactPanel artifact={activeArtifact} onClose={() => setActiveArtifact(null)} />
        </div>
      )}
    </div>
  );
}