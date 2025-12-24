import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'NWPU AskMe',
  description: 'Northwestern Polytechnical University Q&A Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="font-sans">{children}</body>
    </html>
  )
}
