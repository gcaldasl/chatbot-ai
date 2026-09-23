export const SUPPORTED_LOCALES = ["en", "pt", "it"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];

/** Kinds of user-facing failures the app can hit, independent of the exact
 * (English, backend-owned) technical reason — components map these to
 * localized text via `messages.errors`. */
export type ErrorKind =
  | "unsupported-file-type"
  | "file-too-large"
  | "upload-failed"
  | "status-check-failed"
  | "document-not-found"
  | "document-processing-failed"
  | "chat-failed"
  | "llm-unavailable"
  | "unknown";

export type Messages = {
  app: {
    title: string;
    subtitle: string;
  };
  document: {
    heading: string;
    selectPrompt: string;
    acceptedFormats: string;
    statusUploading: string;
    statusProcessing: string;
    statusReady: (chunkCount: number) => string;
    processingHint: string;
    remove: string;
  };
  chat: {
    emptyReady: string;
    emptyProcessing: string;
    emptyIdle: string;
    thinking: string;
    sources: (count: number) => string;
    placeholderReady: string;
    placeholderProcessing: string;
    placeholderIdle: string;
    send: string;
  };
  errors: Record<ErrorKind, string>;
  language: Record<"label" | Locale, string>;
};
