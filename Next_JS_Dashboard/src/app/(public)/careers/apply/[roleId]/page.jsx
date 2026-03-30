"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { getRole } from "@/api/roles"
import { createCandidate } from "@/api/candidates"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  ArrowLeft,
  Upload,
  CheckCircle,
  FileText,
  Sparkles,
} from "lucide-react"
import Link from "next/link"

const inputClass =
  "flex h-11 w-full rounded-xl border border-input bg-background px-3.5 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50"

export default function ApplyPage() {
  const params = useParams()
  const roleId = params.roleId

  const [role, setRole] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
  })
  const [resume, setResume] = useState(null)

  useEffect(() => {
    async function fetchRole() {
      if (!roleId) return
      try {
        const data = await getRole(roleId)
        setRole(data)
      } catch (error) {
        console.error("Failed to fetch role:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchRole()
  }, [roleId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!resume) {
      alert("Please upload a resume")
      return
    }

    setSubmitting(true)
    try {
      const data = new FormData()
      data.append("name", formData.name)
      data.append("email", formData.email)
      if (formData.phone) data.append("phone", formData.phone)
      data.append("resume", resume)
      data.append("role_id", roleId)

      await createCandidate(data)
      setSuccess(true)
    } catch (error) {
      console.error("Failed to submit application:", error)
      const message =
        error.response?.data?.detail ||
        "Failed to submit application. Please try again."
      alert(message)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl space-y-8">
        <Skeleton className="h-9 w-32" />
        <Skeleton className="h-10 w-2/3 max-w-md" />
        <Skeleton className="h-24 w-full rounded-2xl" />
        <Skeleton className="h-96 w-full rounded-2xl" />
      </div>
    )
  }

  if (!role) {
    return (
      <div className="mx-auto max-w-lg rounded-2xl border border-border/60 bg-muted/20 px-6 py-12 text-center">
        <p className="font-medium">Role not found</p>
        <p className="mt-1 text-sm text-muted-foreground">
          This listing may have been closed.
        </p>
        <Button className="mt-6 rounded-xl" asChild>
          <Link href="/careers">Back to careers</Link>
        </Button>
      </div>
    )
  }

  if (success) {
    return (
      <div className="mx-auto max-w-md py-8 text-center sm:py-12">
        <div className="relative overflow-hidden rounded-3xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-background to-background px-6 py-10 shadow-sm">
          <div className="flex justify-center">
            <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-600">
              <CheckCircle className="h-9 w-9" />
            </span>
          </div>
          <h2 className="mt-5 text-2xl font-semibold tracking-tight">
            Application received
          </h2>
          <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
            Thanks for applying to{" "}
            <strong className="text-foreground">{role.title}</strong>. Our team will
            review your profile and reach out if there is a fit.
          </p>
          <Button className="mt-8 w-full rounded-xl sm:w-auto" asChild>
            <Link href="/careers">Browse more roles</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8 pb-8">
      <Button
        variant="ghost"
        size="sm"
        className="-ml-2 rounded-lg text-muted-foreground hover:text-foreground"
        asChild
      >
        <Link href="/careers" className="inline-flex items-center gap-2">
          <ArrowLeft className="h-4 w-4" />
          All positions
        </Link>
      </Button>

      <div className="overflow-hidden rounded-3xl border border-border/60 bg-gradient-to-br from-primary/[0.06] via-background to-violet-500/[0.05] p-6 shadow-sm sm:p-8">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-primary/15 bg-background/70 px-2.5 py-0.5 text-[11px] font-medium text-primary">
          <Sparkles className="h-3 w-3" />
          You are applying for
        </div>
        <h1 className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl">
          {role.title}
        </h1>
        {role.experience_required != null && (
          <p className="mt-2 text-sm text-muted-foreground">
            Ideal experience: {role.experience_required}+ years
          </p>
        )}
        <div className="mt-5 max-w-none text-sm leading-relaxed text-muted-foreground sm:text-[15px]">
          <p className="whitespace-pre-wrap">{role.description}</p>
        </div>
        {role.required_skills?.length > 0 && (
          <div className="mt-5 flex flex-wrap gap-2">
            {role.required_skills.map((skill, i) => (
              <span
                key={i}
                className="rounded-lg border border-border/70 bg-background/80 px-2.5 py-1 text-xs font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        )}
      </div>

      <Card className="overflow-hidden rounded-2xl border-border/60 shadow-sm">
        <CardHeader className="border-b border-border/60 bg-muted/20 px-6 py-5">
          <CardTitle className="text-lg">Your application</CardTitle>
          <CardDescription>
            Tell us who you are and attach your resume. PDF or Word works best.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 sm:p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Full name
                </label>
                <input
                  id="name"
                  className={inputClass}
                  required
                  autoComplete="name"
                  placeholder="Jane Doe"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  className={inputClass}
                  required
                  autoComplete="email"
                  placeholder="you@company.com"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="phone" className="text-sm font-medium">
                Phone <span className="font-normal text-muted-foreground">(optional)</span>
              </label>
              <input
                id="phone"
                type="tel"
                className={inputClass}
                autoComplete="tel"
                placeholder="+1 555 000 0000"
                value={formData.phone}
                onChange={(e) =>
                  setFormData({ ...formData, phone: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <span className="text-sm font-medium">Resume</span>
              <label className="group relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-border/80 bg-muted/30 px-4 py-10 transition-colors hover:border-primary/35 hover:bg-muted/50">
                <input
                  type="file"
                  className="sr-only"
                  accept=".pdf,.docx,.doc"
                  onChange={(e) => setResume(e.target.files?.[0] ?? null)}
                />
                {resume ? (
                  <>
                    <FileText className="h-10 w-10 text-primary" />
                    <p className="mt-3 text-sm font-medium">{resume.name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Click to replace file
                    </p>
                  </>
                ) : (
                  <>
                    <Upload className="h-10 w-10 text-muted-foreground group-hover:text-primary" />
                    <p className="mt-3 text-sm font-medium">
                      Drop your resume or click to browse
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      PDF or DOCX
                    </p>
                  </>
                )}
              </label>
            </div>

            <Button
              type="submit"
              className="h-11 w-full rounded-xl text-base sm:h-12"
              disabled={submitting}
            >
              {submitting ? "Submitting…" : "Submit application"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
