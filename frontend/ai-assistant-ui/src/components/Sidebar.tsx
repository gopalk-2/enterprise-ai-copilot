"use client";

import { useRouter } from "next/navigation";

export default function Sidebar() {
    const router = useRouter();

    return (
        <div className="w-72 bg-slate-900 border-r border-slate-800 h-screen flex flex-col hidden md:flex text-slate-300">
            {/* Branding */}
            <div className="p-6 flex items-center gap-3 border-b border-slate-800/80">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/20">
                    EA
                </div>
                <div className="flex flex-col">
                    <h1 className="font-bold text-white tracking-tight leading-tight">Enterprise AI</h1>
                    <span className="text-[10px] text-slate-500 font-medium uppercase tracking-widest">Internal Secure</span>
                </div>
            </div>

            {/* New Chat Button */}
            <div className="p-5">
                <button
                    onClick={() => window.location.reload()}
                    className="w-full bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800 hover:border-slate-600 hover:text-white text-slate-300 font-medium py-2.5 px-4 rounded-xl shadow-sm transition-all duration-200 flex items-center gap-2 justify-center"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Workspace
                </button>
            </div>

            {/* Navigation / History Placeholder (Optional) */}
            <div className="px-5 py-2">
                <p className="text-xs font-semibold text-slate-600 uppercase tracking-widest mb-3">Recent</p>
                <div className="space-y-1">
                    <div className="px-3 py-2 text-sm text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg cursor-pointer transition-colors truncate">Vacation Policy Query</div>
                    <div className="px-3 py-2 text-sm text-slate-400 hover:bg-slate-800/50 hover:text-white rounded-lg cursor-pointer transition-colors truncate">Engineering Onboarding</div>
                </div>
            </div>

            {/* Spacing to push logout to bottom */}
            <div className="flex-1"></div>

            {/* User Profile & Logout */}
            <div className="p-5 border-t border-slate-800/80 bg-slate-900/50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 text-sm font-bold shadow-inner">
                            U
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-medium text-slate-200">Team Member</span>
                            <span className="text-[10px] text-emerald-400 uppercase tracking-wider font-semibold flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Active
                            </span>
                        </div>
                    </div>
                    <button
                        onClick={() => { localStorage.removeItem("is_logged_in"); router.push("/login"); }}
                        className="text-slate-500 hover:text-white transition-colors p-2 rounded-lg hover:bg-slate-800"
                        title="Sign Out"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
}
