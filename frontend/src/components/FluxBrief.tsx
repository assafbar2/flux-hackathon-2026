import type { BriefSection } from "../types";
import { SourceChips } from "./SourceChips";

type FluxBriefProps = {
  sections: BriefSection[];
};

export function FluxBrief({ sections }: FluxBriefProps) {
  return (
    <section className="brief-grid">
      {sections.map((section) => (
        <article className="brief-card" key={section.title}>
          <h2>{section.title}</h2>
          <p>{section.body}</p>
          <SourceChips sources={section.sources} />
        </article>
      ))}
    </section>
  );
}
