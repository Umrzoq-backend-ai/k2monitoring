import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'School21 Explorer',
  description: 'School21 analytics tree view — Tashkent & Samarkand',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body>{children}</body>
    </html>
  );
}
