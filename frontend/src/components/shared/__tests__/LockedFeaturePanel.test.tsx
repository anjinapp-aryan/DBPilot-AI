import { Database } from "lucide-react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LockedFeaturePanel } from "../LockedFeaturePanel";

describe("LockedFeaturePanel", () => {
  it("renders title, description, and reason", () => {
    render(
      <LockedFeaturePanel
        icon={Database}
        title="No data"
        description="Connect something"
        reason="Backend isn't ready"
      />,
    );
    expect(screen.getByText("No data")).toBeInTheDocument();
    expect(screen.getByText("Connect something")).toBeInTheDocument();
    expect(screen.getByText("Backend isn't ready")).toBeInTheDocument();
  });

  it("fires the CTA callback when clicked", () => {
    const onClick = vi.fn();
    render(
      <LockedFeaturePanel
        icon={Database}
        title="No data"
        description="Connect something"
        cta={{ label: "Add connection", onClick }}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Add connection" }));
    expect(onClick).toHaveBeenCalledOnce();
  });
});
