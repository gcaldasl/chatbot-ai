"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useDocumentUpload } from "@/hooks/useDocumentUpload";

type DocumentContextValue = ReturnType<typeof useDocumentUpload>;

const DocumentContext = createContext<DocumentContextValue | null>(null);

export function DocumentProvider({ children }: { children: ReactNode }) {
  const value = useDocumentUpload();
  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>;
}

export function useDocumentContext(): DocumentContextValue {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error("useDocumentContext must be used within a DocumentProvider");
  }
  return context;
}
