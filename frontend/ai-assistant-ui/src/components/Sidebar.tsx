"use client";

import { useRouter } from "next/navigation";

export default function Sidebar() {
  const router = useRouter();

  return (
    <div className="w-64 h-screen flex-shrink-0 flex-col bg-zinc-950 hidden md:flex select-none">

      {/* Brand */}
      <div className="px-5 pt-6 pb-5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0">
            <svg className="w-4.5 h-4.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
          </div>
          <div>
            <div className="text-white text-sm font-semibold tracking-tight">COGNO AI</div>
            <div className="text-zinc-500 text-[10px] font-medium uppercase tracking-widest mt-0.5">Enterprise</div>
          </div>
        </div>
      </div>

      {/* New Workspace */}
      <div className="px-3 mb-4">
        <button
          onClick={() => window.location.reload()}
          className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/8 transition-all text-sm font-medium group"
        >
          <div className="w-5 h-5 rounded-md border border-zinc-700 flex items-center justify-center group-hover:border-zinc-500 transition-colors">
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
            </svg>
          </div>
          New workspace
        </button>
      </div>

      {/* Divider */}
      <div className="mx-5 border-t border-white/5 mb-4" />

      {/* Recents */}
      <div className="px-5 mb-2">
        <span className="text-[10px] text-zinc-600 font-semibold uppercase tracking-widest">Recents</span>
      </div>
      <div className="px-3 space-y-0.5">
        {["Vacation Policy Query", "Engineering Onboarding"].map((item) => (
          <button
            key={item}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/5 transition-all text-[13px] text-left truncate"
          >
            <svg className="w-3.5 h-3.5 flex-shrink-0 text-zinc-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span className="truncate">{item}</span>
          </button>
        ))}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Status pill */}
      <div className="mx-5 mb-4">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 w-fit">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[11px] text-emerald-400 font-medium">Systems online</span>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-5 border-t border-white/5 mb-4" />

      {/* User */}
      <div className="px-3 pb-5">
        <div className="flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-white/5 transition-colors group">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-zinc-700 flex items-center justify-center text-zinc-300 text-[11px] font-semibold">
              U
            </div>
            <div>
              <div className="text-zinc-300 text-[13px] font-medium">Team Member</div>
              <div className="text-zinc-600 text-[10px]">employee</div>
            </div>
          </div>
          <button
            onClick={() => { localStorage.removeItem("is_logged_in"); router.push("/login"); }}
            className="p-1.5 text-zinc-600 hover:text-zinc-300 hover:bg-white/8 rounded-lg transition-all opacity-0 group-hover:opacity-100"
            title="Sign out"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
