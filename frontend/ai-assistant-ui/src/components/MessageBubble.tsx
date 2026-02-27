"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

interface MessageBubbleProps {
  text: string;
  isUser: boolean;
  time?: string;
}

export default function MessageBubble({ text, isUser, time }: MessageBubbleProps) {
  const [displayedText, setDisplayedText] = useState(isUser ? text : "");

  useEffect(() => {
    // Only animate if it's an AI message and we haven't typed it out yet
    if (!isUser && text) {
      let i = 0;
      const interval = setInterval(() => {
        setDisplayedText(text.slice(0, i + 1));
        i++;
        if (i >= text.length) {
          clearInterval(interval);
        }
      }, 15); // Speed: 15ms per character. Lower is faster.
      
      return () => clearInterval(interval);
    }
  }, [text, isUser]);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
        isUser ? "bg-blue-600 text-white rounded-tr-none" : "bg-white text-gray-800 border rounded-tl-none"
      }`}>
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{displayedText}</ReactMarkdown>
          {/* Visual cursor effect while typing */}
          {!isUser && displayedText.length < text.length && (
            <span className="inline-block w-1.5 h-4 ml-1 bg-gray-400 animate-pulse align-middle" />
          )}
        </div>
        {time && (
          <p className={`text-[10px] mt-2 opacity-70 ${isUser ? "text-right" : "text-left"}`}>
            {time}
          </p>
        )}
      </div>
    </div>
  );
}