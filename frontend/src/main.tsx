import React from "react";
import { createRoot } from "react-dom/client";
import { OnboardPage } from "./pages/Onboard";
import { SetupPage } from "./pages/Setup";
import "./styles.css";

function App() {
  const path = window.location.pathname;
  const workspaceMatch = path.match(/^\/onboard\/([^/]+)$/);

  if (workspaceMatch) {
    return <OnboardPage workspaceId={workspaceMatch[1]} />;
  }

  return <SetupPage />;
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
