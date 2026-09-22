"use client";

import { useRef, useState } from "react";

const ACCEPTED_TYPES = ["text/plain", "application/pdf"];
const ACCEPTED_EXTENSIONS = [".txt", ".pdf"];

type ChatMessage = {
  id: string;
  role: "user";
  content: string;
};

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
  const [fileError, setFileError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!isAcceptedFile(file)) {
      setFileError("Formato não suportado. Envie um arquivo .txt ou .pdf.");
      setSelectedFile(null);
      return;
    }

    setFileError(null);
    setSelectedFile(file);
  }

  function handleRemoveFile() {
    setSelectedFile(null);
    setFileError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function handleSendMessage() {
    const trimmed = chatInput.trim();
    if (!trimmed) return;

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: trimmed },
    ]);
    setChatInput("");
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

            {fileError && (
              <p className="text-xs text-red-600 dark:text-red-400">
                {fileError}
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
                  Faça uma pergunta sobre o documento carregado.
                </p>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className="flex justify-end">
                    <p className="max-w-[75%] rounded-2xl rounded-br-sm bg-zinc-900 px-4 py-2 text-sm text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900">
                      {message.content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="flex items-end gap-2 border-t border-zinc-200 p-4 dark:border-zinc-800">
              <textarea
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                onKeyDown={handleInputKeyDown}
                placeholder="Digite sua pergunta..."
                rows={1}
                className="flex-1 resize-none rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-500 dark:border-zinc-700 dark:text-zinc-100 dark:focus:border-zinc-500"
              />
              <button
                type="button"
                onClick={handleSendMessage}
                disabled={!chatInput.trim()}
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
