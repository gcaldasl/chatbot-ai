import type { Messages } from "@/i18n/types";

export const pt: Messages = {
  app: {
    title: "Agente de Conhecimento",
    subtitle: "Envie um documento e faça perguntas sobre o seu conteúdo.",
  },
  document: {
    heading: "Documento",
    selectPrompt: "Clique para selecionar um arquivo",
    acceptedFormats: ".txt ou .pdf",
    statusUploading: "Enviando...",
    statusProcessing: "Processando...",
    statusReady: (chunkCount) => `Pronto (${chunkCount} trechos)`,
    processingHint: "Isso pode levar alguns minutos para arquivos grandes.",
    remove: "Remover",
  },
  chat: {
    emptyReady: "Faça uma pergunta sobre o documento carregado.",
    emptyProcessing: "Aguarde o processamento do documento...",
    emptyIdle: "Envie um documento para começar a conversa.",
    thinking: "Pensando...",
    sources: (count) => `Fontes (${count})`,
    placeholderReady: "Digite sua pergunta...",
    placeholderProcessing: "Processando documento...",
    placeholderIdle: "Envie um documento primeiro",
    send: "Enviar",
  },
  errors: {
    "unsupported-file-type": "Formato não suportado. Envie um arquivo .txt ou .pdf.",
    "file-too-large": "O arquivo é muito grande.",
    "upload-failed": "Falha ao enviar o documento. Tente novamente.",
    "status-check-failed": "Falha ao verificar o status do documento.",
    "document-not-found": "Documento não encontrado. Envie um documento primeiro.",
    "document-processing-failed": "Algo deu errado ao processar o documento.",
    "chat-failed": "Falha ao consultar o assistente. Tente novamente.",
    "llm-unavailable": "O modelo de linguagem está temporariamente indisponível.",
    unknown: "Algo deu errado. Tente novamente.",
  },
  language: {
    label: "Idioma",
    en: "English",
    pt: "Português",
    it: "Italiano",
  },
};
