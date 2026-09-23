"use client";

import { useLocaleContext } from "@/context/LocaleContext";
import { useChat } from "@/hooks/useChat";
import { ChatInputBar } from "./ChatInputBar";
import { ChatMessageList } from "./ChatMessageList";

export function ChatPanel() {
  const { messages, chatInput, setChatInput, isSending, chatError, sendMessage, handleInputKeyDown } =
    useChat();
  const { messages: t } = useLocaleContext();

  return (
    <section className="flex min-h-[480px] flex-col rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <ChatMessageList messages={messages} isSending={isSending} />

      {chatError && <p className="px-5 text-xs text-red-600 dark:text-red-400">{t.errors[chatError]}</p>}

      <ChatInputBar
        value={chatInput}
        onChange={setChatInput}
        onKeyDown={handleInputKeyDown}
        onSend={sendMessage}
        isSending={isSending}
      />
    </section>
  );
}
