import ChatWindow from "@/components/ChatWindow";
import Sidebar from "@/components/Sidebar";

export default function Home() {
  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <div className="flex-1">
        <ChatWindow />
      </div>
    </div>
  );
}