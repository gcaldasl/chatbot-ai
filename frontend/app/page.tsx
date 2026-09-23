"use client";

import { useRef, useState } from "react";

const ACCEPTED_TYPES = ["text/plain", "application/pdf"];
const ACCEPTED_EXTENSIONS = [".txt", ".pdf"];
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Source = {
  index: number;
  excerpt: string;
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type UploadStatus = "idle" | "uploading" | "ready" | "error";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isAcceptedFile(file: File): boolean {
  if (ACCEPTED_TYPES.includes(file.type)) return true;
  return ACCEPTED_EXTENSIONS.some((ext) =>
    file.name.toLowerCase().endsWith(ext)
  );
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!isAcceptedFile(file)) {
      setUploadStatus("error");
      setUploadError("Formato não suportado. Envie um arquivo .txt ou .pdf.");
      setSelectedFile(null);
      setDocumentId(null);
      return;
    }

    setSelectedFile(file);
    setDocumentId(null);
    setUploadStatus("uploading");
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/api/documents`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail ?? "Falha ao enviar o documento.");
      }

      const data = await response.json();
      setDocumentId(data.id);
      setUploadStatus("ready");
    } catch (error) {
      setUploadStatus("error");
      setUploadError(
        error instanceof Error ? error.message : "Falha ao enviar o documento."
      );
    }
  }

  function handleRemoveFile() {
    setSelectedFile(null);
    setDocumentId(null);
    setUploadStatus("idle");
    setUploadError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function handleSendMessage() {
    const trimmed = chatInput.trim();
    if (!trimmed || !documentId || isSending) return;

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: trimmed },
    ]);
    setChatInput("");
    setChatError(null);
    setIsSending(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: documentId, message: trimmed }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail ?? "Falha ao consultar o assistente.");
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      setChatError(
        error instanceof Error ? error.message : "Falha ao consultar o assistente."
      );
    } finally {
      setIsSending(false);
    }
  }

  function handleInputKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }

  return (
    <div className="flex flex-1 flex-col bg-zinc-50 font-sans dark:bg-black">
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-6 py-10">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Agente de Conhecimento
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Envie um documento e faça perguntas sobre o seu conteúdo.
          </p>
        </header>

        <div className="grid flex-1 grid-cols-1 gap-6 lg:grid-cols-[minmax(0,320px)_1fr]">
          <section className="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-950">
            <h2 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
              Documento
            </h2>

            <label
              htmlFor="document-upload"
              className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-zinc-300 px-4 py-8 text-center transition-colors hover:border-zinc-400 dark:border-zinc-700 dark:hover:border-zinc-600"
            >
              <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                Clique para selecionar um arquivo
              </span>
              <span className="text-xs text-zinc-500 dark:text-zinc-500">
                .txt ou .pdf
              </span>
              <input
                ref={fileInputRef}
                id="document-upload"
                type="file"
                accept=".txt,.pdf,text/plain,application/pdf"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>

            {uploadError && (
              <p className="text-xs text-red-600 dark:text-red-400">
                {uploadError}
              </p>
            )}

            {selectedFile && (
              <div className="flex items-center justify-between gap-2 rounded-lg bg-zinc-100 px-3 py-2 dark:bg-zinc-900">
                <div className="min-w-0">
                  <p className="truncate text-sm text-zinc-800 dark:text-zinc-200">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-500">
                    {formatFileSize(selectedFile.size)}
                    {uploadStatus === "uploading" && " · Enviando..."}
                    {uploadStatus === "ready" && " · Pronto"}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="shrink-0 text-xs font-medium text-zinc-500 hover:text-red-600 dark:text-zinc-400 dark:hover:text-red-400"
                >
                  Remover
                </button>
              </div>
            )}
          </section>

          <section className="flex min-h-[480px] flex-col rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex-1 space-y-3 overflow-y-auto p-5">
              {messages.length === 0 ? (
                <p className="text-sm text-zinc-500 dark:text-zinc-500">
                  {documentId
                    ? "Faça uma pergunta sobre o documento carregado."
                    : "Envie um documento para começar a conversa."}
                </p>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex flex-col ${
                      message.role === "user" ? "items-end" : "items-start"
                    }`}
                  >
                    <p
                      className={
                        message.role === "user"
                          ? "max-w-[75%] rounded-2xl rounded-br-sm bg-zinc-900 px-4 py-2 text-sm text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900"
                          : "max-w-[75%] rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2 text-sm text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
                      }
                    >
                      {message.content}
                    </p>
                    {message.sources && message.sources.length > 0 && (
                      <details className="mt-1 max-w-[75%] text-xs text-zinc-500 dark:text-zinc-400">
                        <summary className="cursor-pointer select-none">
                          Fontes ({message.sources.length})
                        </summary>
                        <ol className="mt-1 space-y-1">
                          {message.sources.map((source) => (
                            <li
                              key={source.index}
                              className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-900"
                            >
                              <span className="font-medium">[{source.index}]</span>{" "}
                              {source.excerpt}
                            </li>
                          ))}
                        </ol>
                      </details>
                    )}
                  </div>
                ))
              )}
              {isSending && (
                <div className="flex justify-start">
                  <p className="max-w-[75%] rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
                    Pensando...
                  </p>
                </div>
              )}
            </div>

            {chatError && (
              <p className="px-5 text-xs text-red-600 dark:text-red-400">
                {chatError}
              </p>
            )}

            <div className="flex items-end gap-2 border-t border-zinc-200 p-4 dark:border-zinc-800">
              <textarea
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                onKeyDown={handleInputKeyDown}
                placeholder={
                  documentId
                    ? "Digite sua pergunta..."
                    : "Envie um documento primeiro"
                }
                disabled={!documentId}
                rows={1}
                className="flex-1 resize-none rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-500 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-100 dark:focus:border-zinc-500"
              />
              <button
                type="button"
                onClick={handleSendMessage}
                disabled={!chatInput.trim() || !documentId || isSending}
                className="shrink-0 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-zinc-50 transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
              >
                Enviar
              </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
