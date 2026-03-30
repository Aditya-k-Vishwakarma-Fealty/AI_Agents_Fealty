"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { LayoutDashboard, Users, Briefcase, Calendar, LayoutGrid } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Pipeline", href: "/pipeline", icon: LayoutGrid },
  { name: "Roles", href: "/roles", icon: Briefcase },
  { name: "Candidates", href: "/candidates", icon: Users },
  { name: "Interviews", href: "/interviews", icon: Calendar },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-border/80 bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80">
      <div className="border-b border-border/60 px-5 py-6">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold shadow-sm">
            HR
          </div>
          <div>
            <p className="text-sm font-semibold leading-tight">Fealty Hiring</p>
            <p className="text-[11px] text-muted-foreground">Admin console</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-0.5 p-3">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0 opacity-90" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
