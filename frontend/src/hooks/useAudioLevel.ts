"use client";

import { useCallback, useRef, useState } from "react";

export interface UseAudioLevelResult {
  levels: number[];
  start: () => Promise<void>;
  stop: () => void;
}

const BAR_COUNT = 24;

export function useAudioLevel(): UseAudioLevelResult {
  const [levels, setLevels] = useState<number[]>(() => Array(BAR_COUNT).fill(0));
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);

  const stop = useCallback(() => {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    audioContextRef.current?.close().catch(() => undefined);
    audioContextRef.current = null;
    setLevels(Array(BAR_COUNT).fill(0));
  }, []);

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;

    const audioContext = new AudioContext();
    audioContextRef.current = audioContext;
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);

    const data = new Uint8Array(analyser.frequencyBinCount);

    const tick = () => {
      analyser.getByteFrequencyData(data);
      const step = Math.floor(data.length / BAR_COUNT) || 1;
      const next: number[] = [];
      for (let i = 0; i < BAR_COUNT; i += 1) {
        next.push(data[i * step] / 255);
      }
      setLevels(next);
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();
  }, []);

  return { levels, start, stop };
}
