"use client";

import { useState } from "react";

export default function ChatInput({ onSend, disabled }: any) {
  const [message, setMessage] = useState("");

  const send = () => {
    if (!message.trim() || disabled) return;
    onSend(message);
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="flex flex-col bg-white border border-slate-200 shadow-[0_8px_30px_rgb(0,0,0,0.06)] rounded-2xl overflow-hidden focus-within:border-indigo-300 focus-within:ring-4 focus-within:ring-indigo-100 transition-all">
      <textarea
        className="w-full max-h-48 min-h-[60px] resize-none outline-none p-4 text-slate-700 placeholder:text-slate-400 bg-transparent text-sm leading-relaxed"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Message Enterprise AI..."
        rows={1}
      />

      <div className="flex justify-between items-center px-3 pb-3 pt-1">
        <div className="flex items-center gap-1">
          <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors" title="Attach Files">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </button>
          <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors" title="Voice Input">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
        </div>

        <button
          onClick={send}
          disabled={!message.trim() || disabled}
          className={`p-2 rounded-lg transition-all flex items-center justify-center ${message.trim() && !disabled
              ? "bg-black text-white hover:bg-slate-800 shadow-md transform active:scale-95"
              : "bg-slate-100 text-slate-300 cursor-not-allowed"
            }`}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </button>
      </div>
    </div>
  );
}