"use client";

import { useState, useRef, useEffect } from "react";

export default function ChatInput({ onSend, disabled }: { onSend: (msg: string) => void; disabled: boolean }) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const send = () => {
    if (!message.trim() || disabled) return;
    onSend(message);
    setMessage("");
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  // Auto-resize textarea
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    // Auto grow
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 180) + "px";
  };

  const canSend = message.trim() && !disabled;

  return (
    <div className={`relative flex flex-col bg-white rounded-2xl border transition-all duration-200 shadow-sm ${
      canSend || !disabled
        ? "border-zinc-300 focus-within:border-zinc-400 focus-within:shadow-md"
        : "border-zinc-200"
    }`}>
      {/* Textarea */}
      <textarea
        ref={textareaRef}
        className="w-full resize-none outline-none px-4 pt-3.5 pb-2 text-[0.9rem] text-zinc-800 placeholder:text-zinc-400 bg-transparent leading-relaxed min-h-[52px] max-h-[180px]"
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "AI is thinking…" : "Ask anything about your enterprise data…"}
        rows={1}
        disabled={disabled}
      />

      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 pb-3">
        <div className="flex items-center gap-0.5">
          <button
            className="p-2 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-lg transition-colors"
            title="Attach files"
            type="button"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </button>
          <button
            className="p-2 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-lg transition-colors"
            title="Voice input"
            type="button"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
        </div>

        <div className="flex items-center gap-2">
          {/* Hint */}
          <span className="text-[11px] text-zinc-300 hidden sm:block">
            {message.trim() ? "↵ send · shift+↵ newline" : ""}
          </span>

          {/* Send button */}
          <button
            onClick={send}
            disabled={!canSend}
            type="button"
            className={`flex items-center justify-center w-8 h-8 rounded-xl transition-all duration-150 ${
              canSend
                ? "bg-zinc-900 text-white hover:bg-zinc-700 shadow-sm active:scale-95"
                : "bg-zinc-100 text-zinc-300 cursor-not-allowed"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}