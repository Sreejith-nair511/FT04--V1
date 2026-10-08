import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CogniShield AI — Dark-Pattern Auditor',
  description: 'See the manipulation. Fix the experience. Evidence-backed dark-pattern auditing for fintech teams.',
  icons: {
    icon: [
      {
        url: '/cognishield-favicon.png',
        sizes: '32x32',
        type: 'image/png',
      },
      {
        url: '/cognishield-favicon-dark.png',
        sizes: '32x32',
        type: 'image/png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/cognishield-logo.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/cognishield-apple-icon.png',
    shortcut: '/cognishield-favicon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
