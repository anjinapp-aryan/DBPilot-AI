import { createHighlighter, type Highlighter } from "shiki";

let highlighterPromise: Promise<Highlighter> | null = null;

function getHighlighter(): Promise<Highlighter> {
  if (!highlighterPromise) {
    highlighterPromise = createHighlighter({
      themes: ["github-dark-default"],
      langs: ["sql", "json", "bash", "python", "typescript", "javascript"],
    });
  }
  return highlighterPromise;
}

export async function highlightCode(code: string, lang: string): Promise<string> {
  const highlighter = await getHighlighter();
  const loadedLangs = highlighter.getLoadedLanguages();
  const safeLang = loadedLangs.includes(lang) ? lang : "sql";
  return highlighter.codeToHtml(code, { lang: safeLang, theme: "github-dark-default" });
}
