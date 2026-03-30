"use client"

import { useEffect, useMemo, useState } from "react"
import { getCandidates } from "@/api/candidates"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { formatStage, formatStatus, stageBadgeClass, statusBadgeClass } from "@/lib/hr-format"
import { Search, RefreshCw, ExternalLink } from "lucide-react"

function TableSkeleton() {
  return (
    <div className="space-y-3 p-4">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  )
}

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState("")
  const [stageFilter, setStageFilter] = useState("")

  const fetchCandidates = async () => {
    setLoading(true)
    try {
      const data = await getCandidates({ limit: 200, skip: 0 })
      setCandidates(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error("Failed to fetch candidates:", error)
      setCandidates([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCandidates()
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return candidates.filter((c) => {
      const matchQ =
        !q ||
        String(c.name || "")
          .toLowerCase()
          .includes(q) ||
        String(c.email || "")
          .toLowerCase()
          .includes(q)
      const matchStage =
        !stageFilter ||
        String(c.current_stage || "").toLowerCase() === stageFilter.toLowerCase()
      return matchQ && matchStage
    })
  }, [candidates, query, stageFilter])

  const stages = useMemo(() => {
    const s = new Set(candidates.map((c) => c.current_stage).filter(Boolean))
    return Array.from(s).sort()
  }, [candidates])

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground mt-1 text-sm max-w-xl">
            Search and filter applicants. Stage and status come from the API (resume pipeline).
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => fetchCandidates()} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" asChild>
            <Link href="/careers" target="_blank" rel="noopener noreferrer">
              <ExternalLink className="mr-2 h-4 w-4" />
              Careers portal
            </Link>
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search by name or email…"
            className="flex h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <select
          className="flex h-10 rounded-lg border border-input bg-background px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring md:w-48"
          value={stageFilter}
          onChange={(e) => setStageFilter(e.target.value)}
        >
          <option value="">All stages</option>
          {stages.map((st) => (
            <option key={st} value={st}>
              {formatStage(st)}
            </option>
          ))}
        </select>
      </div>

      <Card className="border-border/60 shadow-sm overflow-hidden">
        <CardHeader className="border-b border-border/60 bg-muted/20">
          <CardTitle>Applications</CardTitle>
          <CardDescription>
            {loading ? "Loading…" : `${filtered.length} shown${query || stageFilter ? " (filtered)" : ""}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <TableSkeleton />
          ) : (
            <div className="relative w-full overflow-x-auto">
              <table className="w-full caption-bottom text-left text-sm">
                <thead>
                  <tr className="border-b border-border/80 bg-muted/30">
                    <th className="h-11 px-4 font-medium text-muted-foreground">Name</th>
                    <th className="h-11 px-4 font-medium text-muted-foreground">Email</th>
                    <th className="h-11 px-4 font-medium text-muted-foreground">Stage</th>
                    <th className="h-11 px-4 font-medium text-muted-foreground">Status</th>
                    <th className="h-11 px-4 font-medium text-muted-foreground text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((candidate) => (
                    <tr
                      key={candidate.id}
                      className="border-b border-border/60 transition-colors hover:bg-muted/40"
                    >
                      <td className="p-4 align-middle font-medium">{candidate.name}</td>
                      <td className="p-4 align-middle text-muted-foreground">{candidate.email}</td>
                      <td className="p-4 align-middle">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${stageBadgeClass(candidate.current_stage)}`}
                        >
                          {formatStage(candidate.current_stage)}
                        </span>
                      </td>
                      <td className="p-4 align-middle">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${statusBadgeClass(candidate.status)}`}
                        >
                          {formatStatus(candidate.status)}
                        </span>
                      </td>
                      <td className="p-4 align-middle text-right">
                        <Button variant="outline" size="sm" asChild>
                          <Link href={`/candidates/${candidate.id}`}>View</Link>
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={5} className="p-10 text-center text-muted-foreground">
                        No candidates match your filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
