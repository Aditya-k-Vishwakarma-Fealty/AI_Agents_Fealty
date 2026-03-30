"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { submitFeedback, getInterviews } from "@/api/interviews"
import { getCandidates } from "@/api/candidates"
import { getRoles } from "@/api/roles"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Plus, Mic, ArrowRight } from "lucide-react"

export default function InterviewsPage() {
  const [interviews, setInterviews] = useState([])
  const [candidates, setCandidates] = useState([])
  const [roles, setRoles] = useState([])
  const [listLoading, setListLoading] = useState(true)
  const [metaLoading, setMetaLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [formData, setFormData] = useState({
    candidate_id: "",
    role_id: "",
    interviewer_name: "",
    communication_score: 5,
    knowledge_score: 5,
    confidence_score: 5,
    feedback: "",
  })

  const loadLists = async () => {
    setListLoading(true)
    try {
      const data = await getInterviews({ limit: 30, skip: 0 })
      setInterviews(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error("Failed to fetch interviews:", error)
      setInterviews([])
    } finally {
      setListLoading(false)
    }
  }

  const loadMeta = async () => {
    setMetaLoading(true)
    try {
      const [candidatesData, rolesData] = await Promise.all([
        getCandidates({ limit: 500, skip: 0 }),
        getRoles(),
      ])
      setCandidates(Array.isArray(candidatesData) ? candidatesData : [])
      setRoles(Array.isArray(rolesData) ? rolesData : [])
    } catch (error) {
      console.error("Failed to fetch interview form data:", error)
    } finally {
      setMetaLoading(false)
    }
  }

  useEffect(() => {
    loadLists()
    loadMeta()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await submitFeedback({
        ...formData,
        communication_score: Number(formData.communication_score),
        knowledge_score: Number(formData.knowledge_score),
        confidence_score: Number(formData.confidence_score),
        candidate_id: Number(formData.candidate_id),
        role_id: Number(formData.role_id),
      })
      setShowFeedbackForm(false)
      setFormData({
        candidate_id: "",
        role_id: "",
        interviewer_name: "",
        communication_score: 5,
        knowledge_score: 5,
        confidence_score: 5,
        feedback: "",
      })
      await loadLists()
    } catch (error) {
      console.error("Failed to submit feedback:", error)
      alert("Failed to submit feedback")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Interviews</h1>
          <p className="text-muted-foreground mt-1 text-sm max-w-2xl">
            Submit structured feedback and browse recent evaluations. Listing uses the fast{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-[11px]">GET /interviews</code> endpoint.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" asChild size="sm">
            <Link href="/interviews/schedule">Schedule</Link>
          </Button>
          <Button onClick={() => setShowFeedbackForm(!showFeedbackForm)} size="sm">
            {showFeedbackForm ? (
              "Cancel"
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" /> Feedback
              </>
            )}
          </Button>
        </div>
      </div>

      {showFeedbackForm && (
        <Card className="border-border/60 shadow-sm">
          <CardHeader>
            <CardTitle>Submit interview feedback</CardTitle>
            <CardDescription>Scores are 0–10; they feed ranking and final decisions.</CardDescription>
          </CardHeader>
          <CardContent>
            {metaLoading ? (
              <div className="space-y-3 py-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Candidate</label>
                    <select
                      className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      required
                      value={formData.candidate_id}
                      onChange={(e) =>
                        setFormData({ ...formData, candidate_id: e.target.value })
                      }
                    >
                      <option value="">Select candidate</option>
                      {candidates.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium">Role</label>
                    <select
                      className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      required
                      value={formData.role_id}
                      onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                    >
                      <option value="">Select role</option>
                      {roles.map((r) => (
                        <option key={r.id} value={r.id}>
                          {r.title}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid gap-2">
                  <label className="text-sm font-medium">Interviewer name</label>
                  <input
                    className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    required
                    value={formData.interviewer_name}
                    onChange={(e) =>
                      setFormData({ ...formData, interviewer_name: e.target.value })
                    }
                  />
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  {["communication_score", "knowledge_score", "confidence_score"].map((field) => (
                    <div className="grid gap-2" key={field}>
                      <label className="text-sm font-medium capitalize">
                        {field.replace("_", " ")} (0–10)
                      </label>
                      <input
                        type="number"
                        min={0}
                        max={10}
                        step={0.5}
                        className="flex h-10 w-full rounded-lg border border-input px-3 shadow-sm"
                        value={formData[field]}
                        onChange={(e) =>
                          setFormData({ ...formData, [field]: e.target.value })
                        }
                      />
                    </div>
                  ))}
                </div>

                <div className="grid gap-2">
                  <label className="text-sm font-medium">Notes</label>
                  <textarea
                    className="flex min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    required
                    value={formData.feedback}
                    onChange={(e) => setFormData({ ...formData, feedback: e.target.value })}
                  />
                </div>

                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Submitting…" : "Submit evaluation"}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      )}

      <div>
        <div className="flex items-center justify-between gap-4 mb-4">
          <h2 className="text-lg font-semibold tracking-tight">Recent interviews</h2>
          <Button variant="ghost" size="sm" onClick={loadLists} disabled={listLoading}>
            Refresh
          </Button>
        </div>

        {listLoading ? (
          <div className="grid gap-4 md:grid-cols-2">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="border-border/60">
                <CardHeader>
                  <Skeleton className="h-5 w-2/3" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-16 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : interviews.length === 0 ? (
          <Card className="border-dashed border-border/80 bg-muted/10">
            <CardContent className="py-12 text-center text-sm text-muted-foreground">
              No interviews recorded yet. Submit feedback above or schedule a session from the
              schedule page.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {interviews.map((iv) => (
              <Card
                key={iv.id}
                className="border-border/60 shadow-sm transition-shadow hover:shadow-md"
              >
                <CardHeader className="space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base leading-snug">
                      {iv.candidate_name || "Candidate"}{" "}
                      <span className="text-muted-foreground font-normal">·</span>{" "}
                      <span className="font-medium text-foreground">{iv.role_title || "Role"}</span>
                    </CardTitle>
                    {iv.is_voice_interview && (
                      <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-violet-900">
                        <Mic className="h-3 w-3" />
                        Voice
                      </span>
                    )}
                  </div>
                  <CardDescription>
                    {iv.interviewer_name ? `Interviewer: ${iv.interviewer_name}` : "Panel feedback"}
                    {iv.created_date &&
                      ` · ${new Date(iv.created_date).toLocaleString(undefined, {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}`}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex flex-wrap gap-2 text-xs">
                    <span className="rounded-md bg-muted px-2 py-1 font-medium tabular-nums">
                      Overall {Number(iv.overall_score).toFixed(1)}
                    </span>
                    <span className="rounded-md bg-muted/80 px-2 py-1 tabular-nums">
                      Comm {Number(iv.communication_score).toFixed(1)}
                    </span>
                    <span className="rounded-md bg-muted/80 px-2 py-1 tabular-nums">
                      Know {Number(iv.knowledge_score).toFixed(1)}
                    </span>
                    <span className="rounded-md bg-muted/80 px-2 py-1 tabular-nums">
                      Conf {Number(iv.confidence_score).toFixed(1)}
                    </span>
                  </div>
                  {iv.feedback && (
                    <p className="text-sm text-muted-foreground line-clamp-3">{iv.feedback}</p>
                  )}
                  <Button variant="outline" size="sm" asChild>
                    <Link href={`/interviews/${iv.id}`}>
                      Open detail <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
