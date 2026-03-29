"use client";

import React, { useState } from "react";

interface Source {
  source?: string;
  department?: string;
  access_role?: string;
  [key: string]: any;
}

export default function SourcesPanel({ sources }: { sources: Source[] }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors group"
      >
        <svg
          className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? "rotate-90" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span>{sources.length} source{sources.length > 1 ? "s" : ""} cited</span>
      </button>

      {isOpen && (
        <div className="mt-2 space-y-1.5 pl-1 animate-in slide-in-from-top-2 duration-200">
          {sources.map((src, i) => (
            <div
              key={i}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100 hover:border-indigo-200 transition-colors"
            >
              <svg className="w-4 h-4 text-indigo-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-medium text-slate-700 truncate">
                  {src.source || "Unknown Source"}
                </span>
                {src.department && (
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                    {src.department}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
