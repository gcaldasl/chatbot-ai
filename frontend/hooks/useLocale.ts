"use client";

import { useCallback, useEffect, useSyncExternalStore } from "react";
import { DEFAULT_LOCALE, MESSAGES, detectInitialLocale, persistLocale } from "@/i18n";
import type { Locale } from "@/i18n";

// The stored/browser-derived locale is external state unavailable during SSR
// (it lives in localStorage/navigator). useSyncExternalStore is React's
// dedicated API for that: it renders DEFAULT_LOCALE on the server and on the
// client's first pass (avoiding a hydration mismatch), then re-reads the real
// value right after mount.
const listeners = new Set<() => void>();

function subscribe(callback: () => void): () => void {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

function getSnapshot(): Locale {
  return detectInitialLocale();
}

function getServerSnapshot(): Locale {
  return DEFAULT_LOCALE;
}

export function useLocale() {
  const locale = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    persistLocale(next);
    for (const listener of listeners) listener();
  }, []);

  return { locale, setLocale, messages: MESSAGES[locale] };
}
