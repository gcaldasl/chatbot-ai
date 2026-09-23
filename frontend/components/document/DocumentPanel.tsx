"use client";

import { useRef, type ChangeEvent } from "react";
import { useDocumentContext } from "@/context/DocumentContext";
import { formatFileSize } from "@/utils/format";

export function DocumentPanel() {
  const { selectedFile, documentMeta, uploadStatus, uploadError, selectFile, removeFile } =
    useDocumentContext();
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    void selectFile(file);
  }

  function handleRemoveFile() {
    removeFile();
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-950">
      <h2 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">Documento</h2>

      <label
        htmlFor="document-upload"
        className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-zinc-300 px-4 py-8 text-center transition-colors hover:border-zinc-400 dark:border-zinc-700 dark:hover:border-zinc-600"
      >
        <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Clique para selecionar um arquivo
        </span>
        <span className="text-xs text-zinc-500 dark:text-zinc-500">.txt ou .pdf</span>
        <input
          ref={fileInputRef}
          id="document-upload"
          type="file"
          accept=".txt,.pdf,text/plain,application/pdf"
          className="hidden"
          onChange={handleFileChange}
        />
      </label>

      {uploadError && <p className="text-xs text-red-600 dark:text-red-400">{uploadError}</p>}

      {selectedFile && (
        <div className="flex items-center justify-between gap-2 rounded-lg bg-zinc-100 px-3 py-2 dark:bg-zinc-900">
          <div className="min-w-0">
            <p className="truncate text-sm text-zinc-800 dark:text-zinc-200">{selectedFile.name}</p>
            <p className="text-xs text-zinc-500 dark:text-zinc-500">
              {formatFileSize(selectedFile.size)}
              {uploadStatus === "uploading" && " · Enviando..."}
              {uploadStatus === "processing" && " · Processando..."}
              {uploadStatus === "ready" &&
                ` · Pronto${documentMeta ? ` (${documentMeta.chunks} trechos)` : ""}`}
            </p>
            {uploadStatus === "processing" && (
              <p className="text-xs text-zinc-500 dark:text-zinc-500">
                Isso pode levar alguns minutos para arquivos grandes.
              </p>
            )}
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
  );
}
