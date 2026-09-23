import type { Messages } from "@/i18n/types";

export const it: Messages = {
  app: {
    title: "Agente della Conoscenza",
    subtitle: "Carica un documento e fai domande sul suo contenuto.",
  },
  document: {
    heading: "Documento",
    selectPrompt: "Clicca per selezionare un file",
    acceptedFormats: ".txt o .pdf",
    statusUploading: "Caricamento...",
    statusProcessing: "Elaborazione...",
    statusReady: (chunkCount) => `Pronto (${chunkCount} frammenti)`,
    processingHint: "Per file di grandi dimensioni questo può richiedere alcuni minuti.",
    remove: "Rimuovi",
  },
  chat: {
    emptyReady: "Fai una domanda sul documento caricato.",
    emptyProcessing: "Attendere il completamento dell'elaborazione del documento...",
    emptyIdle: "Carica un documento per iniziare la conversazione.",
    thinking: "Sto pensando...",
    sources: (count) => `Fonti (${count})`,
    placeholderReady: "Scrivi la tua domanda...",
    placeholderProcessing: "Elaborazione del documento...",
    placeholderIdle: "Carica prima un documento",
    send: "Invia",
  },
  errors: {
    "unsupported-file-type": "Formato non supportato. Carica un file .txt o .pdf.",
    "file-too-large": "Il file è troppo grande.",
    "upload-failed": "Impossibile caricare il documento. Riprova.",
    "status-check-failed": "Impossibile verificare lo stato del documento.",
    "document-not-found": "Documento non trovato. Carica prima un documento.",
    "document-processing-failed": "Si è verificato un errore durante l'elaborazione del documento.",
    "chat-failed": "Impossibile contattare l'assistente. Riprova.",
    "llm-unavailable": "Il modello linguistico non è temporaneamente disponibile.",
    unknown: "Qualcosa è andato storto. Riprova.",
  },
  language: {
    label: "Lingua",
    en: "English",
    pt: "Português",
    it: "Italiano",
  },
};
