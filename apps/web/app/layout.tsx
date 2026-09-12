import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NGX Research Console",
  description: "A deterministic, regime-aware multi-factor research platform for the Nigerian Exchange.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

