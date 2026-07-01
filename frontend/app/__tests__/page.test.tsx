import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../page";

describe("HomePage", () => {
  it("renders the DBPilot AI heading", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "DBPilot AI" })).toBeInTheDocument();
  });

  it("links to the GitHub repository", () => {
    render(<HomePage />);
    const link = screen.getByRole("link", { name: /view on github/i });
    expect(link).toHaveAttribute("href", "https://github.com/anjinapp-aryan/DBPilot-AI");
  });
});
