"use client";

import { useRouter } from "next/navigation";

export default function Sidebar() {
    const router = useRouter();

    return (
        <div className="w-64 bg-slate-50 border-r border-slate-200 h-screen flex flex-col hidden md:flex">
            {/* Branding */}
            <div className="p-6 flex items-center gap-3 border-b border-slate-200">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md">
                    EA
                </div>
                <h1 className="font-bold text-slate-800 tracking-tight">Enterprise AI</h1>
            </div>

            {/* New Chat Button */}
            <div className="p-4">
                <button
                    onClick={() => window.location.reload()}
                    className="w-full bg-white border border-slate-200 hover:border-blue-400 hover:text-blue-600 text-slate-700 font-medium py-2.5 px-4 rounded-xl shadow-sm transition-all flex items-center gap-2 justify-center"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Workspace
                </button>
            </div>

            {/* Spacing to push logout to bottom */}
            <div className="flex-1"></div>

            {/* User Profile & Logout */}
            <div className="p-4 border-t border-slate-200 bg-slate-100/50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center text-slate-600 text-sm font-bold">
                            U
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-medium text-slate-700">Team Member</span>
                            <span className="text-[10px] text-slate-400 uppercase tracking-wider">Active</span>
                        </div>
                    </div>
                    <button
                        onClick={() => { localStorage.removeItem("is_logged_in"); router.push("/login"); }}
                        className="text-slate-400 hover:text-red-500 transition-colors p-2 rounded-lg hover:bg-slate-200"
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
