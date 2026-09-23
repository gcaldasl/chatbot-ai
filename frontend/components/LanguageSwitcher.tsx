"use client";

import { useLocaleContext } from "@/context/LocaleContext";
import { SUPPORTED_LOCALES, type Locale } from "@/i18n";

const SEGMENT_WIDTH = 40; // px — keep in sync with the `w-10` button width below

const CODE_LABELS: Record<Locale, string> = {
  en: "EN",
  pt: "PT",
  it: "IT",
};

export function LanguageSwitcher() {
  const { locale, setLocale, messages } = useLocaleContext();
  const activeIndex = SUPPORTED_LOCALES.indexOf(locale);

  return (
    <div
      role="group"
      aria-label={messages.language.label}
      className="relative inline-flex items-center rounded-full border border-zinc-200 bg-zinc-100 p-0.5 dark:border-zinc-800 dark:bg-zinc-900"
    >
      <span
        aria-hidden
        className="absolute inset-y-0.5 left-0.5 h-7 w-10 rounded-full bg-white shadow-sm transition-transform duration-200 ease-out dark:bg-zinc-700"
        style={{ transform: `translateX(${activeIndex * SEGMENT_WIDTH}px)` }}
      />
      {SUPPORTED_LOCALES.map((code) => (
        <button
          key={code}
          type="button"
          aria-pressed={locale === code}
          title={messages.language[code]}
          onClick={() => setLocale(code)}
          className={`relative z-10 h-7 w-10 rounded-full text-xs font-medium transition-colors ${
            locale === code
              ? "text-zinc-900 dark:text-zinc-50"
              : "text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
          }`}
        >
          {CODE_LABELS[code]}
        </button>
      ))}
    </div>
  );
}
