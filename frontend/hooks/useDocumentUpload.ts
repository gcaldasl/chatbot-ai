"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, fetchDocumentStatus, uploadDocument } from "@/lib/api";
import { POLL_INTERVAL_MS } from "@/lib/constants";
import type { DocumentMeta, UploadStatus } from "@/types";
import { isAcceptedFile } from "@/utils/fileValidation";

export function useDocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentMeta, setDocumentMeta] = useState<DocumentMeta | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [uploadError, setUploadError] = useState<string | null>(null);

  const pollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeDocumentIdRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (pollTimeoutRef.current) clearTimeout(pollTimeoutRef.current);
    };
  }, []);

  function stopPolling() {
    activeDocumentIdRef.current = null;
    if (pollTimeoutRef.current) {
      clearTimeout(pollTimeoutRef.current);
      pollTimeoutRef.current = null;
    }
  }

  async function pollDocumentStatus(id: string) {
    if (activeDocumentIdRef.current !== id) return;

    try {
      const data = await fetchDocumentStatus(id);
      if (activeDocumentIdRef.current !== id) return;

      if (data.status === "ready") {
        setUploadStatus("ready");
        setDocumentMeta({ characters: data.characters ?? 0, chunks: data.chunks ?? 0 });
      } else if (data.status === "failed") {
        setUploadStatus("error");
        setUploadError(data.error ?? "Falha ao processar o documento.");
      } else {
        pollTimeoutRef.current = setTimeout(() => pollDocumentStatus(id), POLL_INTERVAL_MS);
      }
    } catch (error) {
      if (activeDocumentIdRef.current !== id) return;
      setUploadStatus("error");
      setUploadError(
        error instanceof Error ? error.message : "Falha ao verificar status do documento."
      );
    }
  }

  // Also used by chat when the server rejects a message because the document
  // turned out to still be processing (e.g. a missed poll) — resumes tracking
  // an already-uploaded document instead of only being reachable from upload.
  function resumePolling(id: string) {
    setUploadStatus("processing");
    activeDocumentIdRef.current = id;
    pollDocumentStatus(id);
  }

  async function selectFile(file: File) {
    stopPolling();

    if (!isAcceptedFile(file)) {
      setUploadStatus("error");
      setUploadError("Formato não suportado. Envie um arquivo .txt ou .pdf.");
      setSelectedFile(null);
      setDocumentId(null);
      setDocumentMeta(null);
      return;
    }

    setSelectedFile(file);
    setDocumentId(null);
    setDocumentMeta(null);
    setUploadStatus("uploading");
    setUploadError(null);

    try {
      const data = await uploadDocument(file);
      setDocumentId(data.id);
      resumePolling(data.id);
    } catch (error) {
      setUploadStatus("error");
      setUploadError(
        error instanceof ApiError || error instanceof Error
          ? error.message
          : "Falha ao enviar o documento."
      );
    }
  }

  function removeFile() {
    stopPolling();
    setSelectedFile(null);
    setDocumentId(null);
    setDocumentMeta(null);
    setUploadStatus("idle");
    setUploadError(null);
  }

  return {
    selectedFile,
    documentId,
    documentMeta,
    uploadStatus,
    uploadError,
    selectFile,
    removeFile,
    resumePolling,
  };
}
