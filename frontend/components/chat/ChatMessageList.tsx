"use client";

import { useDocumentContext } from "@/context/DocumentContext";
import { useLocaleContext } from "@/context/LocaleContext";
import type { ChatMessage } from "@/types";
import { ChatMessageBubble } from "./ChatMessageBubble";

type ChatMessageListProps = {
  messages: ChatMessage[];
  isSending: boolean;
};

export function ChatMessageList({ messages, isSending }: ChatMessageListProps) {
  const { uploadStatus } = useDocumentContext();
  const { messages: t } = useLocaleContext();

  return (
    <div className="flex-1 space-y-3 overflow-y-auto p-5">
      {messages.length === 0 ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-500">
          {uploadStatus === "ready"
            ? t.chat.emptyReady
            : uploadStatus === "processing"
            ? t.chat.emptyProcessing
            : t.chat.emptyIdle}
        </p>
      ) : (
        messages.map((message) => <ChatMessageBubble key={message.id} message={message} />)
      )}
      {isSending && (
        <div className="flex justify-start">
          <p className="max-w-[75%] rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
            {t.chat.thinking}
          </p>
        </div>
      )}
    </div>
  );
}
