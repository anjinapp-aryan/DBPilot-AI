"use client";

import { Mic, MicOff } from "lucide-react";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useAudioLevel } from "@/hooks/useAudioLevel";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { cn } from "@/lib/utils";

import { Waveform } from "./Waveform";

export interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  size?: "default" | "lg";
}

export function VoiceButton({ onTranscript, size = "default" }: VoiceButtonProps) {
  const { supported, isListening, transcript, start, stop, reset } = useSpeechRecognition();
  const { levels, start: startLevels, stop: stopLevels } = useAudioLevel();

  useEffect(() => {
    if (transcript) onTranscript(transcript);
  }, [transcript, onTranscript]);

  useEffect(() => {
    return () => stopLevels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleClick = () => {
    if (isListening) {
      stop();
      stopLevels();
      return;
    }
    reset();
    start();
    void startLevels().catch(() => undefined);
  };

  const button = (
    <Button
      type="button"
      variant={isListening ? "default" : "secondary"}
      size="icon"
      disabled={!supported}
      onClick={handleClick}
      aria-pressed={isListening}
      aria-label={isListening ? "Stop voice input" : "Start voice input"}
      className={cn(
        "relative rounded-full transition-transform duration-[var(--duration-base)]",
        size === "lg" ? "size-14" : "size-10",
        isListening && "animate-pulse",
      )}
    >
      {supported ? (
        <Mic className={size === "lg" ? "size-6" : "size-4.5"} />
      ) : (
        <MicOff className={size === "lg" ? "size-6" : "size-4.5"} />
      )}
    </Button>
  );

  return (
    <div className="flex items-center gap-2">
      {supported ? (
        button
      ) : (
        <Tooltip>
          <TooltipTrigger asChild>{button}</TooltipTrigger>
          <TooltipContent>
            Voice input isn&apos;t supported in this browser — try Chrome or Edge.
          </TooltipContent>
        </Tooltip>
      )}
      {isListening && <Waveform levels={levels} />}
    </div>
  );
}
