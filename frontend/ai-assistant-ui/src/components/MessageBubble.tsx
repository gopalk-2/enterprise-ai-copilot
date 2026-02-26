"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

interface MessageBubbleProps {
  text: string;
  isUser: boolean;
}

export default function MessageBubble({ text, isUser }: MessageBubbleProps) {
  const [displayedText, setDisplayedText] = useState(isUser ? text : "");

  useEffect(() => {
    if (!isUser) {
      let i = 0;
      const interval = setInterval(() => {
        setDisplayedText(text.slice(0, i + 1));
        i++;
        if (i >= text.length) clearInterval(interval);
      }, 10); // Adjust speed here
      return () => clearInterval(interval);
    }
  }, [text, isUser]);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[80%] p-4 rounded-2xl shadow-sm ${
        isUser ? "bg-blue-600 text-white rounded-tr-none" : "bg-white text-gray-800 border rounded-tl-none"
      }`}>
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{displayedText}</ReactMarkdown>
          {!isUser && displayedText.length < text.length && (
            <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse align-middle" />
          )}
        </div>
      </div>
    </div>
  );
}