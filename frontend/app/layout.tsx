import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "DBPilot AI — Your AI Copilot for Databases",
  description:
    "Connect a database, ask questions in plain English, and get safe, explained, executed SQL.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
