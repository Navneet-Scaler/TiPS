import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TIPS — Talent Intelligence & Personal Signals",
  description: "Personal AI opportunity intelligence radar.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-base-bg text-base-text font-sans antialiased">{children}</body>
    </html>
  );
}
