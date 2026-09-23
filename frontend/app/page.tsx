import { AppHeader } from "@/components/AppHeader";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { DocumentPanel } from "@/components/document/DocumentPanel";
import { DocumentProvider } from "@/context/DocumentContext";
import { LocaleProvider } from "@/context/LocaleContext";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col bg-zinc-50 font-sans dark:bg-black">
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-6 py-10">
        <LocaleProvider>
          <AppHeader />

          <DocumentProvider>
            <div className="grid flex-1 grid-cols-1 gap-6 lg:grid-cols-[minmax(0,320px)_1fr]">
              <DocumentPanel />
              <ChatPanel />
            </div>
          </DocumentProvider>
        </LocaleProvider>
      </main>
    </div>
  );
}
