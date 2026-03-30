"use client"

import { useCallback, useEffect, useState } from "react"
import Link from "next/link"
import { getCandidates } from "@/api/candidates"
import { PipelineBoard } from "@/components/pipeline/PipelineBoard"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { RefreshCw } from "lucide-react"

export default function PipelinePage() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [boardKey, setBoardKey] = useState(0)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getCandidates({ limit: 500, skip: 0 })
      setCandidates(Array.isArray(data) ? data : [])
      setBoardKey((k) => k + 1)
    } catch (e) {
      console.error(e)
      setCandidates([])
      setBoardKey((k) => k + 1)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Pipeline board</h1>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            Drag cards between stages to update candidate progress. Changes save
            to the API immediately — ideal for agencies running multiple reqs in
            parallel.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => load()}
            disabled={loading}
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
          <Button size="sm" variant="outline" asChild>
            <Link href="/dashboard">Dashboard</Link>
          </Button>
        </div>
      </div>

      <Card className="border-border/60 shadow-sm">
        <CardHeader>
          <CardTitle>Kanban</CardTitle>
          <CardDescription>
            Six stages from submission to final. Only active statuses are shown
            on cards; drag to advance or correct pipeline placement.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-[420px] w-full rounded-xl" />
          ) : (
            <PipelineBoard
              key={boardKey}
              initialCandidates={candidates}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
