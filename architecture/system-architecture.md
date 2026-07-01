# System Architecture Diagram

Source of truth for DBPilot AI's architecture diagrams. Rendered copies are
embedded in [README.md](../README.md) and [docs/architecture.md](../docs/architecture.md).

## Full System Diagram

```mermaid
flowchart TB
    subgraph Client["Client"]
        Browser["Browser<br/>(Voice input via Web Speech API)"]
    end

    subgraph Vercel["Vercel"]
        FE["Frontend<br/>Next.js (App Router, TypeScript)"]
    end

    subgraph BackendHost["Railway / Render"]
        API["FastAPI REST + WebSocket API"]
        AuthZ["Auth / Rate Limiting"]
        Orchestrator["Multi-Agent Orchestrator"]

        subgraph Agents["Agents"]
            SD["Schema Discovery Agent"]
            T2S["Text-to-SQL Agent"]
            VAL["SQL Validator Agent"]
            EXEC["SQL Executor Agent"]
            EXP["SQL Explainer Agent"]
            CHART["Chart Agent"]
        end
    end

    subgraph External["External Services"]
        DeepSeek["DeepSeek LLM API"]
    end

    subgraph Data["Data Layer"]
        AppDB[("App DB — Neon PostgreSQL<br/>users, connections, conversations, audit log")]
        TargetDB[("Target DB(s) — user-connected PostgreSQL")]
    end

    Browser <--> FE
    FE <-->|HTTPS / WebSocket| API
    API --> AuthZ
    API --> Orchestrator
    Orchestrator --> SD --> TargetDB
    Orchestrator --> T2S --> DeepSeek
    Orchestrator --> VAL
    VAL --> EXEC --> TargetDB
    Orchestrator --> EXP --> DeepSeek
    Orchestrator --> CHART
    API --> AppDB
```

## Text-to-SQL Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as Backend API
    participant T2S as Text-to-SQL Agent
    participant VAL as Validator Agent
    participant EXEC as Executor Agent
    participant DB as Target DB

    U->>FE: Asks question (text or voice)
    FE->>API: POST /api/v1/query
    API->>T2S: question + schema context + history
    T2S->>API: candidate SQL
    API->>VAL: candidate SQL
    alt rejected
        VAL-->>API: rejection + reason
        API-->>FE: show rejection, ask to clarify
    else approved
        VAL-->>API: approved SQL
        API->>EXEC: approved SQL
        EXEC->>DB: run (row-limited, timeout-bound)
        DB-->>EXEC: result rows
        EXEC-->>API: result rows
        API-->>FE: results + explanation + chart
    end
```

## Diagram Conventions

- Diagrams are authored as [Mermaid](https://mermaid.js.org/) so they render
  natively on GitHub without external tooling.
- Keep this file as the single source of truth; copy relevant excerpts into
  `README.md` / `docs/architecture.md` rather than diverging them.
