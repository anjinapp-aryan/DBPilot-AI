"use client";

import { useEffect, useState } from "react";

/**
 * Persists a panel's collapsed state in localStorage so nav/right-panel
 * preference survives a reload. `key` must be unique per panel.
 *
 * The initial read happens post-mount (not in the lazy useState
 * initializer) so server and client render the same default first,
 * avoiding a hydration mismatch; the one-time setState-in-effect this
 * requires is an intentional exception to the "no setState in effects"
 * lint rule, not an oversight.
 */
export function useCollapsiblePanel(key: string, defaultCollapsed = false) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(key);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (stored !== null) setCollapsed(stored === "true");
    setHydrated(true);
  }, [key]);

  useEffect(() => {
    if (!hydrated) return;
    window.localStorage.setItem(key, String(collapsed));
  }, [key, collapsed, hydrated]);

  return { collapsed, setCollapsed, toggle: () => setCollapsed((c) => !c) };
}
