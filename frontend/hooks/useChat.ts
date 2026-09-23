"use client";

import { useState, type KeyboardEvent } from "react";
import { useDocumentContext } from "@/context/DocumentContext";
import { ApiError, sendChatMessage } from "@/lib/api";
import type { ChatMessage } from "@/types";

export function useChat() {
  const { documentId, uploadStatus, resumePolling } = useDocumentContext();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  async function sendMessage() {
    const trimmed = chatInput.trim();
    if (!trimmed || uploadStatus !== "ready" || !documentId || isSending) return;

    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setChatInput("");
    setChatError(null);
    setIsSending(true);

    try {
      const data = await sendChatMessage(documentId, trimmed);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        // Local state said "ready" but the server disagrees (e.g. a missed poll)
        // — not a real error, so resume polling instead of scaring the user with
        // red text, and give their message back to resend.
        setMessages((prev) => prev.filter((message) => message.id !== userMessage.id));
        setChatInput(trimmed);
        resumePolling(documentId);
        return;
      }

      setChatError(error instanceof Error ? error.message : "Falha ao consultar o assistente.");
    } finally {
      setIsSending(false);
    }
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage();
    }
  }

  return {
    messages,
    chatInput,
    setChatInput,
    isSending,
    chatError,
    sendMessage,
    handleInputKeyDown,
  };
}
