export type Source = {
  index: number;
  excerpt: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

export type UploadStatus = "idle" | "uploading" | "processing" | "ready" | "error";

export type DocumentMeta = {
  characters: number;
  chunks: number;
};

export type DocumentStatus = "processing" | "ready" | "failed";

export type UploadDocumentResponse = {
  id: string;
  filename: string;
  status: DocumentStatus;
};

export type DocumentStatusResponse = {
  id: string;
  filename: string;
  status: DocumentStatus;
  characters: number | null;
  chunks: number | null;
  error: string | null;
};

export type ChatResponse = {
  answer: string;
  sources: Source[];
};
