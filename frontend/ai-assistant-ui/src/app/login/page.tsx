"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const login = async () => {
    setLoading(true);
    const url = `http://127.0.0.1:8000/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;

    try {
      const res = await fetch(url, { method: "POST" });
      if (!res.ok) throw new Error("Invalid credentials");

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      router.push("/");
    } catch (err) {
      alert("Login failed. Please check your username and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="p-10 bg-white border border-slate-200 shadow-2xl rounded-3xl w-full max-w-md">
        <div className="text-center mb-10">
          <div className="inline-block p-4 bg-blue-50 rounded-2xl mb-4">
            <span className="text-3xl">🚀</span>
          </div>
          <h2 className="text-3xl font-extrabold text-slate-800">Welcome Back</h2>
          <p className="text-slate-500 mt-2">Sign in to your AI workspace</p>
        </div>

        <div className="space-y-5">
          <div>
            <label className="text-sm font-semibold text-slate-700 ml-1">Username</label>
            <input
              placeholder="Enter your username"
              className="mt-1 w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all"
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-slate-700 ml-1">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="mt-1 w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            onClick={login}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-200 transition-all transform active:scale-[0.98] disabled:opacity-70"
          >
            {loading ? "Authenticating..." : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}