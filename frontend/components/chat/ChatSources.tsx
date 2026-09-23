import type { Source } from "@/types";

type ChatSourcesProps = {
  sources: Source[];
};

export function ChatSources({ sources }: ChatSourcesProps) {
  if (sources.length === 0) return null;

  return (
    <details className="mt-1 max-w-[75%] text-xs text-zinc-500 dark:text-zinc-400">
      <summary className="cursor-pointer select-none">Fontes ({sources.length})</summary>
      <ol className="mt-1 space-y-1">
        {sources.map((source) => (
          <li key={source.index} className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-900">
            <span className="font-medium">[{source.index}]</span> {source.excerpt}
          </li>
        ))}
      </ol>
    </details>
  );
}
