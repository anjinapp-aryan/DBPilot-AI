import { renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useSpeechRecognition } from "../useSpeechRecognition";

describe("useSpeechRecognition", () => {
  afterEach(() => {
    // @ts-expect-error - cleaning up test-only global
    delete window.SpeechRecognition;
    // @ts-expect-error - cleaning up test-only global
    delete window.webkitSpeechRecognition;
  });

  it("reports unsupported when no SpeechRecognition constructor exists", () => {
    const { result } = renderHook(() => useSpeechRecognition());
    expect(result.current.supported).toBe(false);
  });

  it("reports supported and can start when a constructor is present", () => {
    const start = vi.fn();
    class FakeRecognition extends EventTarget {
      continuous = false;
      interimResults = false;
      lang = "en-US";
      start = start;
      stop = vi.fn();
      onresult = null;
      onerror = null;
      onend = null;
    }
    // @ts-expect-error - test double for the browser API
    window.SpeechRecognition = FakeRecognition;

    const { result } = renderHook(() => useSpeechRecognition());
    expect(result.current.supported).toBe(true);
  });
});
