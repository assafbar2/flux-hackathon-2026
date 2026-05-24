import { useEffect, useMemo, useState } from "react";
import { Loader2, ShieldCheck } from "lucide-react";
import { Chat } from "../components/Chat";
import { FluxBrief } from "../components/FluxBrief";
import type { BriefSection, ChatMessage } from "../types";

type OnboardPageProps = {
  workspaceId: string;
};

export function OnboardPage({ workspaceId }: OnboardPageProps) {
  const [brief, setBrief] = useState<Record<string, BriefSection> | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("Who actually owns the auth system?");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadBrief() {
      setLoading(true);
      const response = await fetch(`/api/brief/${workspaceId}`);
      const payload = await response.json();
      setBrief(payload.brief);
      setLoading(false);
    }
    void loadBrief();
  }, [workspaceId]);

  const sections = useMemo(() => {
    if (!brief) return [];
    return [brief.now, brief.people, brief.moves, brief.landmines];
  }, [brief]);

  async function send(message = input) {
    if (!message.trim()) return;
    setMessages((current) => [...current, { role: "user", body: message }]);
    setInput("");
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workspace_id: workspaceId, message })
    });
    const payload = await response.json();
    setMessages((current) => [
      ...current,
      {
        role: "assistant",
        body: payload.answer,
        sources: payload.sources,
        action: payload.action
      }
    ]);
  }

  return (
    <main className="workspace">
      <header className="topbar">
        <div>
          <div className="mark">Flux</div>
          <p>New hire brief</p>
        </div>
        <div className="status">
          <ShieldCheck size={16} aria-hidden="true" />
          Demo mode
        </div>
      </header>
      {loading ? (
        <section className="loading">
          <Loader2 size={28} aria-hidden="true" />
          Building influence graph
        </section>
      ) : (
        <FluxBrief sections={sections} />
      )}
      <Chat input={input} messages={messages} onInputChange={setInput} onSend={(message) => void send(message)} />
    </main>
  );
}
