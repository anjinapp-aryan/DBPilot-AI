export function Waveform({ levels }: { levels: number[] }) {
  return (
    <div className="flex h-8 items-center gap-0.5" role="img" aria-label="Live microphone waveform">
      {levels.map((level, i) => (
        <span
          key={i}
          className="w-1 rounded-full bg-accent transition-[height] duration-100"
          style={{ height: `${Math.max(4, level * 32)}px` }}
        />
      ))}
    </div>
  );
}
