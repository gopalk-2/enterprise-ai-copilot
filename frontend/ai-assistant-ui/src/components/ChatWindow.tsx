"use client";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

export default function ChatWindow() {
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
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
  }, [messages, isLoading]);

  const sendMessage = async (msg: string) => {
    if (!msg.trim()) return;
    const token = localStorage.getItem("token");

    const userMsg = {
      text: msg,
      user: true,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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
      let assistantMessage = "";

      // Add an initial empty assistant message to the state
      setMessages((prev) => [
        ...prev,
        {
          text: "",
          user: false,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
      ]);

      // Read the stream chunk by chunk
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        assistantMessage += chunk;

        // Update the last message (the assistant's current response) with the appended chunk
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            text: assistantMessage,
          };
          return newMessages;
        });
      }
    } catch (error) {
      setMessages((prev) => [...prev, { text: "⚠️ Server connection lost.", user: false }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-white relative">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative max-w-5xl mx-auto w-full border-x border-slate-100 shadow-[0_0_40px_-15px_rgba(0,0,0,0.05)]">

        {/* Production Header */}
        <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md px-8 py-5 flex justify-between items-center border-b border-slate-100">
          <div className="flex items-center gap-3 md:hidden">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <h1 className="text-lg font-bold text-slate-800">Enterprise Assistant</h1>
          </div>
          <div className="hidden md:block"></div> {/* Spacer for desktop since branding is in sidebar */}
          <button
            onClick={() => { localStorage.removeItem("is_logged_in"); router.push("/login"); }}
            className="text-xs font-semibold text-slate-400 hover:text-red-500 transition-colors uppercase tracking-wider md:hidden"
          >
            Logout
          </button>
        </header>

        {/* Scrollable Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-10 space-y-8 scrollbar-hide">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full opacity-40">
              <span className="text-5xl mb-4">✨</span>
              <p className="text-slate-900 font-medium">Start a conversation with your data.</p>
            </div>
          )}

          {messages.map((m, i) => (
            <MessageBubble key={i} text={m.text} isUser={m.user} time={m.time} />
          ))}

          {isLoading && (
            <div className="flex justify-start items-center gap-2 text-slate-400 text-sm pl-4">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"></div>
                <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:0.4s]"></div>
              </div>
            </div>
          )}
        </div>

        {/* Catchy Input Area */}
        <footer className="p-6 bg-gradient-to-t from-white via-white to-transparent">
          <div className="max-w-3xl mx-auto relative bg-white border border-slate-200 rounded-2xl shadow-xl p-2 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </div>
          <p className="text-[10px] text-center text-slate-400 mt-4 uppercase tracking-[0.2em] font-bold">
            Powered by RAG Architecture
          </p>
        </footer>
      </div>
    </div>
  );
}