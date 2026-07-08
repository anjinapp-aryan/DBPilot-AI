import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TooltipProvider } from "@/components/ui/tooltip";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

import HomePage from "../(shell)/page";

function renderWithQueryClient(ui: React.ReactElement) {
  const client = new QueryClient();
  return render(
    <QueryClientProvider client={client}>
      <TooltipProvider>{ui}</TooltipProvider>
    </QueryClientProvider>,
  );
}

describe("HomePage", () => {
  it("renders the greeting and quick actions", () => {
    renderWithQueryClient(<HomePage />);
    expect(
      screen.getByText(/what would you like to know about your data today/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /quick actions/i })).toBeInTheDocument();
  });

  it("shows locked empty states for recent databases and conversations", () => {
    renderWithQueryClient(<HomePage />);
    expect(screen.getByText(/no databases connected yet/i)).toBeInTheDocument();
    expect(screen.getByText(/no saved conversations yet/i)).toBeInTheDocument();
  });
});
