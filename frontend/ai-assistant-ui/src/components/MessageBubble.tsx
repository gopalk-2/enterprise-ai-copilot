"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MessageBubbleProps {
  text: string;
  isUser: boolean;
  time?: string;
}

export default function MessageBubble({ text, isUser, time }: MessageBubbleProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${isUser ? "bg-blue-600 text-white rounded-tr-none" : "bg-white text-gray-800 border rounded-tl-none"
        }`}>
        <div className="prose prose-sm max-w-none prose-p:leading-relaxed prose-headings:font-bold prose-headings:mb-2 prose-ul:list-disc prose-ol:list-decimal prose-li:my-0.5">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: ({ node, href, children, ...props }) => {
                // Intercept citation links to render as our custom badges
                // We check for '#source' as instructed to the LLM, or fallback to any relative path just in case
                if (href === '#source' || (href && !href.startsWith('http') && !href.startsWith('mailto'))) {
                  const docName = String(children);
                  return (
                    <span
                      onClick={() => alert(`Opening source document:\n${docName}`)}
                      className="inline-flex items-center gap-1 px-2.5 py-[2px] rounded-full text-[10px] font-medium bg-blue-100 text-blue-800 cursor-pointer hover:bg-blue-200 transition-colors mx-1 whitespace-nowrap align-middle shadow-sm border border-blue-200"
                      title={`View Source: ${docName}`}
                    >
                      <svg className="w-3 h-3 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      {docName}
                    </span>
                  );
                }
                // Fallback for normal links
                return <a href={href} className="text-blue-600 hover:text-blue-800 underline transition-colors" target="_blank" rel="noopener noreferrer" {...props}>{children}</a>;
              }
            }}
          >
            {text}
          </ReactMarkdown>
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