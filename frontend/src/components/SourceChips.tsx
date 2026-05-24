export function SourceChips({ sources = [] }: { sources?: string[] }) {
  return (
    <div className="sources">
      {sources.map((source) => (
        <span key={source}>{source}</span>
      ))}
    </div>
  );
}
