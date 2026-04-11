import ChatWindow from "@/components/ChatWindow";
import Sidebar from "@/components/Sidebar";

export default function Home() {
  return (
    <div className="flex h-screen bg-white overflow-hidden">
      <Sidebar />
      {/* Main area — flex-1 so the artifact panel inside ChatWindow can expand */}
      <div className="flex-1 min-w-0 flex overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  );
}