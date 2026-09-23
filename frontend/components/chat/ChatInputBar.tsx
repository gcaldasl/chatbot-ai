"use client";

import type { KeyboardEvent } from "react";
import { useDocumentContext } from "@/context/DocumentContext";
import { useLocaleContext } from "@/context/LocaleContext";

type ChatInputBarProps = {
  value: string;
  onChange: (value: string) => void;
  onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  isSending: boolean;
};

export function ChatInputBar({ value, onChange, onKeyDown, onSend, isSending }: ChatInputBarProps) {
  const { uploadStatus } = useDocumentContext();
  const { messages } = useLocaleContext();
  const isReady = uploadStatus === "ready";

  return (
    <div className="flex items-end gap-2 border-t border-zinc-200 p-4 dark:border-zinc-800">
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={onKeyDown}
        placeholder={
          isReady
            ? messages.chat.placeholderReady
            : uploadStatus === "processing"
            ? messages.chat.placeholderProcessing
            : messages.chat.placeholderIdle
        }
        disabled={!isReady}
        rows={1}
        className="flex-1 resize-none rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-500 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-100 dark:focus:border-zinc-500"
      />
      <button
        type="button"
        onClick={onSend}
        disabled={!value.trim() || !isReady || isSending}
        className="shrink-0 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-zinc-50 transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
      >
        {messages.chat.send}
      </button>
    </div>
  );
}
