import type { ChatMessage } from "@/types";
import { ChatSources } from "./ChatSources";

type ChatMessageBubbleProps = {
  message: ChatMessage;
};

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
      <p
        className={
          isUser
            ? "max-w-[75%] rounded-2xl rounded-br-sm bg-zinc-900 px-4 py-2 text-sm text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900"
            : "max-w-[75%] rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2 text-sm text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
        }
      >
        {message.content}
      </p>
      {message.sources && <ChatSources sources={message.sources} />}
    </div>
  );
}
