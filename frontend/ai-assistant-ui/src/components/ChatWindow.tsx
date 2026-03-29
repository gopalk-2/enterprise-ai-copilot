"use client";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

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
  status?: string;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const isLoggedIn = localStorage.getItem("is_logged_in");
    if (!isLoggedIn) router.push("/login");
  }, [router]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isLoading, agentStatus]);

  const sendMessage = async (msg: string) => {
    if (!msg.trim()) return;

    const userMsg: Message = {
      text: msg,
      user: true,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setAgentStatus(null);

    let assistantMessage = "";
    let collectedSources: any[] = [];
    let collectedUIComponents: UIComponent[] = [];
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

      // Add initial empty assistant message
      setMessages((prev) => [
        ...prev,
        {
          text: "",
          user: false,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          sources: [],
          uiComponents: [],
        },
      ]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // Keep the last potentially incomplete line in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const event = JSON.parse(line);

            switch (event.type) {
              case "status":
                setAgentStatus(event.content);
                break;

              case "token":
                assistantMessage += event.content;
                if (Date.now() - lastRenderTime > 50) {
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1] = {
                      ...newMessages[newMessages.length - 1],
                      text: assistantMessage,
                    };
                    return newMessages;
                  });
                  lastRenderTime = Date.now();
                }
                break;

              case "sources":
                collectedSources = event.content || [];
                setMessages((prev) => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    sources: collectedSources,
                  };
                  return newMessages;
                });
                break;

              case "ui_component":
                collectedUIComponents.push({
                  component: event.component,
                  data: event.data,
                });
                setMessages((prev) => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    uiComponents: [...collectedUIComponents],
                  };
                  return newMessages;
                });
                break;

              case "done":
                setMessages((prev) => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    text: assistantMessage,
                  };
                  return newMessages;
                });
                setAgentStatus(null);
                break;
            }
          } catch (e) {
            // If JSON parsing fails, treat the line as a raw text token (backward compat)
            assistantMessage += line;
            if (Date.now() - lastRenderTime > 50) {
              setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = {
                  ...newMessages[newMessages.length - 1],
                  text: assistantMessage,
                };
                return newMessages;
              });
              lastRenderTime = Date.now();
            }
          }
        }
      }
    } catch (error) {
      setMessages((prev) => [...prev, { text: "⚠️ Server connection lost. Please try again.", user: false }]);
    } finally {
      setIsLoading(false);
      setAgentStatus(null);
      // Ensure final message text is flushed completely
      setMessages((prev) => {
        const newMessages = [...prev];
        if (newMessages.length > 0 && !newMessages[newMessages.length - 1].user) {
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            text: assistantMessage,
          };
        }
        return newMessages;
      });
    }
  };

  const suggestions = [
    { title: "Summarize Policy", desc: "Latest remote work guidelines" },
    { title: "Analyze Revenue", desc: "Q3 performance metrics" },
    { title: "Check SLA Status", desc: "Severity 1 compliance" },
    { title: "Review Code", desc: "Check tech stack compliance" },
  ];

  return (
    <div className="flex h-full bg-white relative">
      <div className="flex-1 flex flex-col relative max-w-4xl mx-auto w-full">

        {/* Mobile Header */}
        <header className="md:hidden sticky top-0 z-10 bg-white/80 backdrop-blur-md px-6 py-4 flex justify-between items-center border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-md">EA</div>
            <h1 className="font-bold text-slate-800 tracking-tight">Enterprise AI</h1>
          </div>
          <button
            onClick={() => { localStorage.removeItem("is_logged_in"); router.push("/login"); }}
            className="text-xs font-semibold text-slate-400 hover:text-red-500 transition-colors uppercase tracking-wider"
          >
            Logout
          </button>
        </header>

        {/* Messages Area */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 py-8 space-y-8 pb-32 scrollbar-hide">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[60vh] animate-in fade-in duration-700">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-xl shadow-indigo-500/20 mb-8">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.792 0-5.484-.478-8.067-1.387-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">How can I help you today?</h2>
              <p className="text-slate-500 mb-12 text-center max-w-sm">Securely connect to your enterprise data, trigger workflows, analyze data, or ask questions.</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl px-4">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(s.title + ": " + s.desc)}
                    className="flex flex-col items-start p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 hover:shadow-md transition-all text-left group"
                  >
                    <span className="font-semibold text-slate-700 text-sm group-hover:text-indigo-600 transition-colors">{s.title}</span>
                    <span className="text-slate-500 text-xs mt-1">{s.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((m, i) => (
                <MessageBubble
                  key={i}
                  text={m.text}
                  isUser={m.user}
                  time={m.time}
                  sources={m.sources}
                  uiComponents={m.uiComponents}
                />
              ))}

              {/* Agent Status Indicator */}
              {(isLoading || agentStatus) && (
                <div className="flex justify-start items-center gap-3 pl-4 md:pl-16 py-4">
                  <div className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100 shadow-sm">
                    <div className="flex gap-1.5">
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                    </div>
                    {agentStatus && (
                      <span className="text-xs font-medium text-indigo-600 animate-pulse">
                        {agentStatus}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Input Area */}
        <footer className="absolute bottom-0 left-0 right-0 p-4 md:p-8 bg-gradient-to-t from-white via-white to-transparent pt-20">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={sendMessage} disabled={isLoading} />
            <p className="text-[10px] text-center text-slate-400 mt-4 uppercase tracking-[0.2em] font-semibold">
              Secure Enterprise AI &bull; Multi-Agent System &bull; AI generated content may be inaccurate
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}