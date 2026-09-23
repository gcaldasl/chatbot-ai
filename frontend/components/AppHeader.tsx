"use client";

import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useLocaleContext } from "@/context/LocaleContext";

export function AppHeader() {
  const { messages } = useLocaleContext();

  return (
    <header className="flex items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          {messages.app.title}
        </h1>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{messages.app.subtitle}</p>
      </div>
      <LanguageSwitcher />
    </header>
  );
}
