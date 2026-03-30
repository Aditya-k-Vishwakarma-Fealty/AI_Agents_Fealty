"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { getDashboardStats } from "@/api/stats"
import { getRecruiterInsights } from "@/api/insights"
import { formatStage } from "@/lib/hr-format"
import { Users, Briefcase, Calendar, ArrowRight, Lightbulb } from "lucide-react"

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-4 w-64 max-w-full" />
      </div>
      <Skeleton className="h-20 w-full rounded-lg" />
      <Skeleton className="h-16 w-full rounded-lg" />
      <Skeleton className="h-48 w-full rounded-lg" />
    </div>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [insights, setInsights] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      setLoading(true)
      setError(null)
      const results = await Promise.allSettled([
        getDashboardStats(),
        getRecruiterInsights(),
      ])
      if (cancelled) return
      const [st, ins] = results
      if (st.status === "fulfilled") {
        setStats(st.value)
      } else {
        console.error("Failed to fetch dashboard stats:", st.reason)
        setStats(null)
        setError("Could not load dashboard. Check API URL and server.")
      }
      if (ins.status === "fulfilled") {
        setInsights(ins.value)
      } else {
        setInsights(null)
      }
      setLoading(false)
    }
    run()
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return <DashboardSkeleton />
  }

  if (error || !stats) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/5 px-5 py-6 text-center">
        <p className="text-sm text-destructive font-medium">{error || "No data"}</p>
        <p className="text-xs text-muted-foreground mt-2">
          For local development, run the API on port 8000 or set{" "}
          <code className="rounded bg-muted px-1 py-0.5 text-[11px]">NEXT_PUBLIC_API_URL</code>.
        </p>
      </div>
    )
  }

  const recent = Array.isArray(stats.recent_activity) ? stats.recent_activity : []
  const recentInterviews = Array.isArray(stats.recent_interviews)
    ? stats.recent_interviews
    : []

  const recommended = Array.isArray(insights?.recommended_actions)
    ? insights.recommended_actions
    : []
  const stalledCount = Array.isArray(insights?.stalled_candidates)
    ? insights.stalled_candidates.length
    : 0

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between sm:gap-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Snapshot of candidates, roles, and recent activity.
          </p>
        </div>
        <nav className="flex flex-wrap items-center gap-x-1 text-sm text-muted-foreground">
          <Link href="/pipeline" className="hover:text-foreground">
            Pipeline
          </Link>
          <span aria-hidden className="px-1">
            ·
          </span>
          <Link href="/candidates" className="hover:text-foreground">
            Candidates
          </Link>
          <span aria-hidden className="px-1">
            ·
          </span>
          <Link href="/roles" className="hover:text-foreground">
            Roles
          </Link>
          <span aria-hidden className="px-1">
            ·
          </span>
          <Link href="/interviews" className="hover:text-foreground">
            Interviews
          </Link>
        </nav>
      </div>

      <div className="grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-border/80 bg-border/60">
        <div className="bg-background px-3 py-3 sm:px-4 sm:py-3.5">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Users className="h-3.5 w-3.5 shrink-0" />
            <span className="text-[11px] font-medium uppercase tracking-wide">
              Candidates
            </span>
          </div>
          <p className="text-2xl font-semibold tabular-nums mt-1">{stats.candidates}</p>
        </div>
        <div className="bg-background px-3 py-3 sm:px-4 sm:py-3.5">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Briefcase className="h-3.5 w-3.5 shrink-0" />
            <span className="text-[11px] font-medium uppercase tracking-wide">Roles</span>
          </div>
          <p className="text-2xl font-semibold tabular-nums mt-1">{stats.roles}</p>
        </div>
        <div className="bg-background px-3 py-3 sm:px-4 sm:py-3.5">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="h-3.5 w-3.5 shrink-0" />
            <span className="text-[11px] font-medium uppercase tracking-wide">
              Interviews
            </span>
          </div>
          <p className="text-2xl font-semibold tabular-nums mt-1">{stats.interviews}</p>
        </div>
      </div>

      {insights && (
        <div className="rounded-lg border border-border/70 bg-muted/30 px-4 py-3 text-sm">
          <div className="flex gap-2">
            <Lightbulb className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
            <div className="min-w-0 space-y-2">
              <p className="text-muted-foreground leading-snug">{insights.summary}</p>
              {recommended.length > 0 && (
                <ul className="space-y-1.5">
                  {recommended.slice(0, 2).map((a, idx) => (
                    <li key={idx} className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                      <span className="font-medium text-foreground">{a.title}</span>
                      {a.href && (
                        <Link
                          href={a.href}
                          className="text-xs text-primary hover:underline shrink-0"
                        >
                          Go
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              {stalledCount > 0 && (
                <p className="text-xs text-muted-foreground">
                  {stalledCount} stalled —{" "}
                  <Link href="/pipeline" className="text-primary hover:underline">
                    review pipeline
                  </Link>
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      <Card className="border-border/60 shadow-none">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium">Recent activity</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 pt-0 sm:grid-cols-2 sm:gap-8">
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Applicants</p>
            {recent.length === 0 ? (
              <p className="text-sm text-muted-foreground">No applications yet.</p>
            ) : (
              <ul className="space-y-2">
                {recent.slice(0, 4).map((row) => (
                  <li key={row.id} className="flex items-center justify-between gap-2 text-sm">
                    <span className="truncate font-medium">{row.name}</span>
                    <span className="shrink-0 text-xs text-muted-foreground">
                      {formatStage(row.stage)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <Button variant="link" className="h-auto px-0 pt-2 text-xs" asChild>
              <Link href="/candidates">
                All candidates <ArrowRight className="ml-1 h-3 w-3" />
              </Link>
            </Button>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Interviews</p>
            {recentInterviews.length === 0 ? (
              <p className="text-sm text-muted-foreground">No interviews recorded yet.</p>
            ) : (
              <ul className="space-y-2">
                {recentInterviews.slice(0, 3).map((iv) => (
                  <li key={iv.id} className="flex items-center justify-between gap-2 text-sm">
                    <span className="min-w-0 truncate">
                      {iv.candidate_name || "Candidate"}
                      <span className="text-muted-foreground font-normal">
                        {" "}
                        · {Number(iv.overall_score).toFixed(1)}
                      </span>
                    </span>
                    <Link
                      href={`/interviews/${iv.id}`}
                      className="shrink-0 text-xs text-primary hover:underline"
                    >
                      Open
                    </Link>
                  </li>
                ))}
              </ul>
            )}
            <Button variant="link" className="h-auto px-0 pt-2 text-xs" asChild>
              <Link href="/interviews">
                All interviews <ArrowRight className="ml-1 h-3 w-3" />
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
