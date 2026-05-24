export type BriefSection = {
  title: string;
  body: string;
  sources: string[];
};

export type ChatAction = {
  type: string;
  issue_id: string;
  project: string;
  username: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  body: string;
  sources?: string[];
  action?: ChatAction;
  actionResult?: string;
};
