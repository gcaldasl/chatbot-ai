"use client";

import { useEffect, useRef, useState } from "react";
import type { ErrorKind } from "@/i18n";
import { ApiError, fetchDocumentStatus, uploadDocument } from "@/lib/api";
import { POLL_INTERVAL_MS } from "@/lib/constants";
import type { DocumentMeta, UploadStatus } from "@/types";
import { isAcceptedFile } from "@/utils/fileValidation";

function uploadErrorKind(error: unknown): ErrorKind {
  if (error instanceof ApiError) {
    if (error.status === 400) return "unsupported-file-type";
    if (error.status === 413) return "file-too-large";
  }
  return "upload-failed";
}

function statusCheckErrorKind(error: unknown): ErrorKind {
  if (error instanceof ApiError && error.status === 404) return "document-not-found";
  return "status-check-failed";
}

export function useDocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentMeta, setDocumentMeta] = useState<DocumentMeta | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [uploadError, setUploadError] = useState<ErrorKind | null>(null);
  // The backend's own (English) reason, kept only as optional secondary/technical
  // detail alongside the localized `uploadError` — never shown as the primary message.
  const [uploadErrorDetail, setUploadErrorDetail] = useState<string | null>(null);

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
        setUploadError("document-processing-failed");
        setUploadErrorDetail(data.error);
      } else {
        pollTimeoutRef.current = setTimeout(() => pollDocumentStatus(id), POLL_INTERVAL_MS);
      }
    } catch (error) {
      if (activeDocumentIdRef.current !== id) return;
      setUploadStatus("error");
      setUploadError(statusCheckErrorKind(error));
      setUploadErrorDetail(error instanceof Error ? error.message : null);
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
      setUploadError("unsupported-file-type");
      setUploadErrorDetail(null);
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
    setUploadErrorDetail(null);

    try {
      const data = await uploadDocument(file);
      setDocumentId(data.id);
      resumePolling(data.id);
    } catch (error) {
      setUploadStatus("error");
      setUploadError(uploadErrorKind(error));
      setUploadErrorDetail(error instanceof Error ? error.message : null);
    }
  }

  function removeFile() {
    stopPolling();
    setSelectedFile(null);
    setDocumentId(null);
    setDocumentMeta(null);
    setUploadStatus("idle");
    setUploadError(null);
    setUploadErrorDetail(null);
  }

  return {
    selectedFile,
    documentId,
    documentMeta,
    uploadStatus,
    uploadError,
    uploadErrorDetail,
    selectFile,
    removeFile,
    resumePolling,
  };
}
