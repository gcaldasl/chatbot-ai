import { it } from "@/i18n/locales/it";
import { en } from "@/i18n/locales/en";
import { pt } from "@/i18n/locales/pt";
import { type Locale, type Messages, SUPPORTED_LOCALES } from "@/i18n/types";

export { SUPPORTED_LOCALES };
export type { ErrorKind, Locale, Messages } from "@/i18n/types";

export const DEFAULT_LOCALE: Locale = "pt";

export const MESSAGES: Record<Locale, Messages> = { en, pt, it };

export function isLocale(value: string): value is Locale {
  return (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

const STORAGE_KEY = "locale";

/** Stored preference, then browser language, then DEFAULT_LOCALE. Client-only
 * (uses localStorage/navigator) — callers must guard for SSR. */
export function detectInitialLocale(): Locale {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && isLocale(stored)) return stored;
  } catch {
    // localStorage can throw in private-browsing/blocked-storage contexts.
  }

  for (const lang of window.navigator.languages ?? [window.navigator.language]) {
    const candidate = lang.slice(0, 2).toLowerCase();
    if (isLocale(candidate)) return candidate;
  }

  return DEFAULT_LOCALE;
}

export function persistLocale(locale: Locale): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    // Best-effort; a failed write just means the preference won't survive a reload.
  }
}
