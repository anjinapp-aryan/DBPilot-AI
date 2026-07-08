import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ErDiagramPage from "../(shell)/database/er-diagram/page";
import PerformancePage from "../(shell)/database/performance/page";
import QueryStudioPage from "../(shell)/database/query-studio/page";
import SchemaExplorerPage from "../(shell)/database/schema/page";

describe("locked database pages", () => {
  it("Schema Explorer shows a locked empty state, not fabricated data", () => {
    render(<SchemaExplorerPage />);
    expect(screen.getByRole("heading", { name: "Schema Explorer" })).toBeInTheDocument();
    expect(screen.getByText(/schema discovery isn't available yet/i)).toBeInTheDocument();
  });

  it("SQL Studio shows a locked empty state", () => {
    render(<QueryStudioPage />);
    expect(screen.getByText(/sql execution isn't available yet/i)).toBeInTheDocument();
  });

  it("ER Diagram shows a locked empty state", () => {
    render(<ErDiagramPage />);
    expect(screen.getByText(/no schema to diagram yet/i)).toBeInTheDocument();
  });

  it("Performance Analyzer shows a locked empty state", () => {
    render(<PerformancePage />);
    expect(screen.getByText(/no performance data yet/i)).toBeInTheDocument();
  });
});
