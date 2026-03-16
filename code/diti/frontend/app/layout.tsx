import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Bug Hunter - AI-Powered Code Analysis',
  description: 'Detect and explain bugs in C++ code using advanced AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
