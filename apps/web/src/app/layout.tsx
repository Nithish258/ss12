import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'QUAICU - AI-Mediated Group Decisions',
  description: 'AI-mediated group decision-making platform for collaborative teams',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
