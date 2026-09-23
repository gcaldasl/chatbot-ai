import { API_URL } from "@/lib/constants";
import type {
  ChatResponse,
  DocumentStatusResponse,
  UploadDocumentResponse,
} from "@/types";

/** Thrown for any non-2xx response. `message` is the backend's own (English)
 * detail text when available — treat it as technical/secondary information,
 * not localized UI copy. Callers should pick user-facing text from
 * `messages.errors` based on `status` instead of displaying `message`
 * directly. */
export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function extractErrorMessage(response: Response): Promise<string> {
  const body = await response.json().catch(() => null);
  return body?.detail ?? response.statusText ?? `HTTP ${response.status}`;
}

export async function uploadDocument(file: File): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await extractErrorMessage(response));
  }

  return response.json();
}

export async function fetchDocumentStatus(id: string): Promise<DocumentStatusResponse> {
  const response = await fetch(`${API_URL}/api/documents/${id}`);

  if (!response.ok) {
    throw new ApiError(response.status, await extractErrorMessage(response));
  }

  return response.json();
}

export async function sendChatMessage(documentId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, message }),
  });

  if (!response.ok) {
    throw new ApiError(response.status, await extractErrorMessage(response));
  }

  return response.json();
}
