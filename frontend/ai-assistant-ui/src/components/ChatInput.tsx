"use client";

import { useState } from "react";

export default function ChatInput({ onSend }: any) {
  const [message, setMessage] = useState("");

  const send = () => {
    if (!message) return;
    onSend(message);
    setMessage("");
  };

  return (
    <div className="flex gap-2 p-4 border-t">
      <input
        className="flex-1 border rounded px-3 py-2"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask something..."
      />
      <button
        onClick={send}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Send
      </button>
    </div>
  );
}