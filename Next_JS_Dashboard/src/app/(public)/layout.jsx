import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function PublicLayout({ children }) {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/70">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
          <Link
            href="/careers"
            className="flex items-center gap-2.5 transition-opacity hover:opacity-90"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground shadow-sm">
              F
            </span>
            <div className="leading-tight">
              <span className="block text-sm font-semibold tracking-tight">
                Fealty Careers
              </span>
              <span className="hidden text-[11px] text-muted-foreground sm:block">
                Open roles
              </span>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="text-muted-foreground" asChild>
              <Link href="/careers">Jobs</Link>
            </Button>
            <Button size="sm" asChild>
              <Link href="/dashboard" target="_blank" rel="noopener noreferrer">
                Team login
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-12">{children}</main>

      <footer className="border-t border-border/60 bg-muted/20">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-8 text-center text-xs text-muted-foreground sm:flex-row sm:text-left">
          <p>© {new Date().getFullYear()} Fealty. All rights reserved.</p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link href="/careers" className="hover:text-foreground">
              Open positions
            </Link>
            <Link href="/dashboard" className="hover:text-foreground" target="_blank" rel="noopener noreferrer">
              Recruiter console
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
