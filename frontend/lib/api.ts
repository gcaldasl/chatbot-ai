import { API_URL } from "@/lib/constants";
import type {
  ChatResponse,
  DocumentStatusResponse,
  UploadDocumentResponse,
} from "@/types";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function extractErrorMessage(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => null);
  return body?.detail ?? fallback;
}

export async function uploadDocument(file: File): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await extractErrorMessage(response, "Falha ao enviar o documento."));
  }

  return response.json();
}

export async function fetchDocumentStatus(id: string): Promise<DocumentStatusResponse> {
  const response = await fetch(`${API_URL}/api/documents/${id}`);

  if (!response.ok) {
    throw new ApiError(response.status, "Falha ao verificar status do documento.");
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
    throw new ApiError(response.status, await extractErrorMessage(response, "Falha ao consultar o assistente."));
  }

  return response.json();
}
