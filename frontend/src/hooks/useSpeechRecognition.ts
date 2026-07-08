"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  getSpeechRecognitionCtor,
  type SpeechRecognitionLike,
} from "@/lib/speech/speechRecognitionSupport";

export interface UseSpeechRecognitionResult {
  supported: boolean;
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  start: () => void;
  stop: () => void;
  reset: () => void;
}

export function useSpeechRecognition(): UseSpeechRecognitionResult {
  const [Ctor, setCtor] = useState<(new () => SpeechRecognitionLike) | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Browser support can only be detected client-side. Defaulting to `null`
  // (unsupported) for the very first render keeps it identical to the
  // server-rendered markup, avoiding a hydration mismatch; this effect
  // then resolves the real value right after mount.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setCtor(() => getSpeechRecognitionCtor());
  }, []);

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
    };
  }, []);

  const start = useCallback(() => {
    if (!Ctor) {
      setError("Voice input isn't supported in this browser — try Chrome or Edge.");
      return;
    }

    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = typeof navigator !== "undefined" ? navigator.language : "en-US";

    recognition.onresult = (event) => {
      let finalText = "";
      let interimText = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript;
        } else {
          interimText += result[0].transcript;
        }
      }
      if (finalText) setTranscript((prev) => `${prev}${finalText}`);
      setInterimTranscript(interimText);
    };

    recognition.onerror = (event) => {
      setError(event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript("");
    };

    recognitionRef.current = recognition;
    setError(null);
    setIsListening(true);
    recognition.start();
  }, [Ctor]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const reset = useCallback(() => {
    setTranscript("");
    setInterimTranscript("");
    setError(null);
  }, []);

  return {
    supported: Ctor !== null,
    isListening,
    transcript,
    interimTranscript,
    error,
    start,
    stop,
    reset,
  };
}
