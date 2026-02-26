"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

export default function ChatWindow() {
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const sendMessage = async (msg: string) => {
    if (!msg.trim()) return;

    const userMsg = { text: msg, user: true, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlbXBsb3llZSIsInJvbGUiOiJlbXBsb3llZSIsImV4cCI6MTc3MjE1MTgwMn0.QHllaMKsNp1E8fZfeifOrAo3o5ZIRbCgf61CgNC11tM"}`,
        },
        body: JSON.stringify({ query: msg }),
      });

      const data = await res.json();
      
      setMessages((prev) => [
        ...prev,
        { 
          text: data.answer || data.response || data.agent_response, 
          user: false,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
      ]);
    } catch (error) {
      setMessages((prev) => [...prev, { text: "⚠️ Connection error. Please check your backend.", user: false, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Modern Header */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-gray-800">Enterprise AI</h1>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-xs text-gray-500 font-medium">System Active</span>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-3 opacity-60">
             <div className="bg-blue-100 p-4 rounded-full">🤖</div>
             <p className="text-gray-600 font-medium">Hello! How can I assist with your data today?</p>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.user ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
              m.user ? "bg-blue-600 text-white rounded-tr-none" : "bg-white text-gray-800 border rounded-tl-none"
            }`}>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{m.text}</ReactMarkdown>
              </div>
              <p className={`text-[10px] mt-2 opacity-70 ${m.user ? "text-right" : "text-left"}`}>
                {m.time}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 animate-pulse rounded-2xl p-4 text-gray-500 text-sm">
              AI is analyzing...
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <footer className="bg-white border-t p-4 md:p-6 shadow-2xl">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
          <p className="text-center text-[10px] text-gray-400 mt-3">
            Internal Enterprise Assistant • Next.js + FastAPI RAG Stack
          </p>
        </div>
      </footer>
    </div>
  );
}