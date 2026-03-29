"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SourcesPanel from "./SourcesPanel";
import DynamicRenderer from "./DynamicRenderer";

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
}

export default function MessageBubble({ text, isUser, time, sources, uiComponents }: MessageBubbleProps) {
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex gap-4 max-w-[85%] md:max-w-[75%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>

        {/* Avatar */}
        <div className="flex-shrink-0 mt-1">
          {isUser ? (
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-white text-xs font-bold shadow-sm">
              U
            </div>
          ) : (
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-indigo-500/20">
              EA
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className="flex flex-col min-w-0">
          <div className={`
            px-5 py-4 rounded-2xl shadow-sm
            ${isUser
              ? "bg-slate-800 text-white rounded-tr-sm"
              : "bg-transparent text-slate-800 hover:bg-slate-50/50 transition-colors"
            }
          `}>
            <div className={`prose prose-sm max-w-none prose-p:leading-relaxed prose-headings:font-bold prose-headings:mb-2 prose-ul:list-disc prose-ol:list-decimal prose-li:my-1 ${isUser ? "prose-invert" : ""}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  a: ({ node, href, children, ...props }) => {
                    if (href === '#source' || (href && !href.startsWith('http') && !href.startsWith('mailto'))) {
                      const docName = String(children);
                      return (
                        <span
                          onClick={() => alert(`Opening source document:\n${docName}`)}
                          className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 text-indigo-700 cursor-pointer hover:bg-indigo-100 transition-colors mx-1 whitespace-nowrap align-middle shadow-sm border border-indigo-200/50"
                          title={`View Source: ${docName}`}
                        >
                          <svg className="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          {docName}
                        </span>
                      );
                    }
                    return <a href={href} className={`${isUser ? "text-blue-300 hover:text-blue-200" : "text-indigo-600 hover:text-indigo-800"} underline transition-colors font-medium`} target="_blank" rel="noopener noreferrer" {...props}>{children}</a>;
                  }
                }}
              >
                {text}
              </ReactMarkdown>
            </div>
          </div>

          {/* Dynamic UI Components (charts, tables, etc.) */}
          {!isUser && uiComponents && uiComponents.length > 0 && (
            <DynamicRenderer components={uiComponents} />
          )}

          {/* Sources Panel */}
          {!isUser && sources && sources.length > 0 && (
            <SourcesPanel sources={sources} />
          )}

          {/* Timestamp */}
          {time && (
            <div className={`flex mt-1.5 items-center gap-2 ${isUser ? "justify-end" : "justify-start pl-1"}`}>
              <span className="text-[10px] text-slate-400 font-medium">
                {time}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}