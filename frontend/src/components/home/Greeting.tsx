function getTimeGreeting(hour: number): string {
  if (hour < 5) return "Working late";
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export function Greeting() {
  const greeting = getTimeGreeting(new Date().getHours());

  return (
    <div className="space-y-1.5">
      <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
        {greeting}.
      </h1>
      <p className="text-base text-muted-foreground">
        What would you like to know about your data today?
      </p>
    </div>
  );
}
