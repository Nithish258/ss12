import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'QUAICU - AI-Mediated Group Decisions',
  description: 'AI-mediated group decision-making platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
