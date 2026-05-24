import { useState } from "react";
import { ArrowRight, CheckCircle2, Info } from "lucide-react";

export function SetupPage() {
  const [gitlabToken, setGitlabToken] = useState("");
  const [gitlabUsername, setGitlabUsername] = useState("newhire");
  const [notionUrl, setNotionUrl] = useState("");
  const [hireLink, setHireLink] = useState("");
  const [error, setError] = useState("");
  const usingDemoData = !gitlabToken.trim() || !notionUrl.trim();

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setHireLink("");
    const response = await fetch("/api/setup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gitlab_token: gitlabToken || "demo-token",
        notion_url: notionUrl || "https://notion.so/demo",
        gitlab_username: gitlabUsername || "newhire"
      })
    });
    if (!response.ok) {
      setError("Setup failed. Check the backend and try again.");
      return;
    }
    const payload = await response.json();
    setHireLink(payload.hire_link);
  }

  return (
    <main className="shell setup-shell">
      <section className="intro">
        <div className="mark">Flux</div>
        <h1>The org as it runs, not as it's drawn.</h1>
        <p>Provision a new-hire link from GitLab activity and the HR-maintained team guide.</p>
      </section>
      <form className="panel setup-form" onSubmit={submit}>
        <label>
          GitLab token
          <input value={gitlabToken} onChange={(event) => setGitlabToken(event.target.value)} placeholder="GitLab token" />
        </label>
        <label>
          GitLab username
          <input value={gitlabUsername} onChange={(event) => setGitlabUsername(event.target.value)} placeholder="newhire" />
        </label>
        <label>
          Notion team guide URL
          <input value={notionUrl} onChange={(event) => setNotionUrl(event.target.value)} placeholder="https://notion.so/..." />
        </label>
        {usingDemoData && (
          <div className="demo-note">
            <Info size={16} aria-hidden="true" />
            <span>Using deployed demo data when GitLab token or Notion URL are blank.</span>
          </div>
        )}
        <button type="submit">
          Generate link
          <ArrowRight size={18} aria-hidden="true" />
        </button>
        {error && <p className="error">{error}</p>}
        {hireLink && (
          <div className="result">
            <CheckCircle2 size={18} aria-hidden="true" />
            <a href={hireLink.replace("http://localhost:5173", "")}>{hireLink}</a>
          </div>
        )}
      </form>
    </main>
  );
}
