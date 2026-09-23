import type { Messages } from "@/i18n/types";

export const en: Messages = {
  app: {
    title: "Knowledge Agent",
    subtitle: "Upload a document and ask questions about its content.",
  },
  document: {
    heading: "Document",
    selectPrompt: "Click to select a file",
    acceptedFormats: ".txt or .pdf",
    statusUploading: "Uploading...",
    statusProcessing: "Processing...",
    statusReady: (chunkCount) => `Ready (${chunkCount} chunks)`,
    processingHint: "This can take a few minutes for large files.",
    remove: "Remove",
  },
  chat: {
    emptyReady: "Ask a question about the uploaded document.",
    emptyProcessing: "Waiting for the document to finish processing...",
    emptyIdle: "Upload a document to start the conversation.",
    thinking: "Thinking...",
    sources: (count) => `Sources (${count})`,
    placeholderReady: "Type your question...",
    placeholderProcessing: "Processing document...",
    placeholderIdle: "Upload a document first",
    send: "Send",
  },
  errors: {
    "unsupported-file-type": "Unsupported format. Please upload a .txt or .pdf file.",
    "file-too-large": "The file is too large.",
    "upload-failed": "Failed to upload the document. Please try again.",
    "status-check-failed": "Failed to check the document's status.",
    "document-not-found": "Document not found. Please upload a document first.",
    "document-processing-failed": "Something went wrong while processing the document.",
    "chat-failed": "Failed to reach the assistant. Please try again.",
    "llm-unavailable": "The language model is temporarily unavailable.",
    unknown: "Something went wrong. Please try again.",
  },
  language: {
    label: "Language",
    en: "English",
    pt: "Português",
    it: "Italiano",
  },
};
