import { ChatPanel } from "@/components/chat/ChatPanel";
import { DocumentPanel } from "@/components/document/DocumentPanel";
import { DocumentProvider } from "@/context/DocumentContext";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col bg-zinc-50 font-sans dark:bg-black">
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-6 py-10">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Agente de Conhecimento
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Envie um documento e faça perguntas sobre o seu conteúdo.
          </p>
        </header>

        <DocumentProvider>
          <div className="grid flex-1 grid-cols-1 gap-6 lg:grid-cols-[minmax(0,320px)_1fr]">
            <DocumentPanel />
            <ChatPanel />
          </div>
        </DocumentProvider>
      </main>
    </div>
  );
}
