import { ArrowRight, GitPullRequestArrow } from "lucide-react";
import type { ChatMessage } from "../types";
import { SourceChips } from "./SourceChips";

type ChatProps = {
  input: string;
  messages: ChatMessage[];
  onInputChange: (value: string) => void;
  onSend: (message?: string) => void;
};

const demoQuestions = [
  "Who owns auth?",
  "How do I ship fast?",
  "Anything I shouldn't say in standup?",
  "Assign issue #412 to me"
];

export function Chat({ input, messages, onInputChange, onSend }: ChatProps) {
  return (
    <section className="chat-panel">
      <div className="question-row">
        {demoQuestions.map((question) => (
          <button type="button" className="prompt" key={question} onClick={() => onSend(question)}>
            {question}
          </button>
        ))}
      </div>
      <div className="messages">
        {messages.map((message, index) => (
          <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
            <p>{message.body}</p>
            <SourceChips sources={message.sources} />
            {message.action && (
              <button type="button" className="confirm">
                <GitPullRequestArrow size={16} aria-hidden="true" />
                Confirm assignment
              </button>
            )}
          </div>
        ))}
      </div>
      <form
        className="chat-input"
        onSubmit={(event) => {
          event.preventDefault();
          onSend();
        }}
      >
        <input value={input} onChange={(event) => onInputChange(event.target.value)} />
        <button type="submit">
          Send
          <ArrowRight size={18} aria-hidden="true" />
        </button>
      </form>
    </section>
  );
}
