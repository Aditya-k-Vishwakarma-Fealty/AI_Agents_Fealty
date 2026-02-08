import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function PublicLayout({ children }) {
    return (
        <div className="min-h-screen bg-background font-sans antialiased">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container mx-auto flex h-14 items-center px-4">
                    <div className="mr-4 md:flex">
                        <Link href="/careers" className="mr-6 flex items-center space-x-2">
                            <span className="font-bold sm:inline-block">
                                HR Hiring System
                            </span>
                        </Link>
                    </div>
                    <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                        <nav className="flex items-center space-x-2">
                            <Link href="/dashboard" target="_blank" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                                Admin Login
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>
            <main className="container mx-auto py-6 px-4">
                {children}
            </main>
        </div>
    )
}
