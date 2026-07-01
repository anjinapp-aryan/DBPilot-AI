const PHASES = [
  { name: "Project bootstrap", status: "In progress" },
  { name: "Schema discovery", status: "Planned" },
  { name: "Text-to-SQL", status: "Planned" },
  { name: "SQL validation", status: "Planned" },
  { name: "SQL execution", status: "Planned" },
];

export default function HomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "3rem 1.5rem",
        textAlign: "center",
        gap: "1.5rem",
      }}
    >
      <h1 style={{ fontSize: "2.5rem" }}>DBPilot AI</h1>
      <p style={{ color: "var(--muted)", fontSize: "1.125rem", maxWidth: 560 }}>
        Your AI Copilot for Databases. Connect a database, ask a question in plain English, and get
        safe, explained, executed SQL.
      </p>
      <ul
        style={{
          listStyle: "none",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
          textAlign: "left",
        }}
      >
        {PHASES.map((phase) => (
          <li key={phase.name} style={{ color: "var(--foreground)" }}>
            <span style={{ color: "var(--accent)" }}>
              {phase.status === "In progress" ? "▸" : "·"}
            </span>{" "}
            {phase.name} — <span style={{ color: "var(--muted)" }}>{phase.status}</span>
          </li>
        ))}
      </ul>
      <a href="https://github.com/anjinapp-aryan/DBPilot-AI" target="_blank" rel="noreferrer">
        View on GitHub →
      </a>
    </main>
  );
}
