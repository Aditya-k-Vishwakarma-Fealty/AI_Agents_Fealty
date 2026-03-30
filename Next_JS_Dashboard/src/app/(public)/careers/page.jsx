"use client"

import { useEffect, useState } from "react"
import { getRoles } from "@/api/roles"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
  ArrowRight,
  Briefcase,
  MapPin,
  Sparkles,
  Clock,
} from "lucide-react"

function CareersSkeleton() {
  return (
    <div className="space-y-10">
      <div className="space-y-4 text-center">
        <Skeleton className="mx-auto h-6 w-32 rounded-full" />
        <Skeleton className="mx-auto h-10 w-80 max-w-full" />
        <Skeleton className="mx-auto h-4 w-96 max-w-full" />
      </div>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm"
          >
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="mt-3 h-4 w-1/2" />
            <Skeleton className="mt-6 h-20 w-full" />
            <Skeleton className="mt-4 h-9 w-full rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  )
}

export default function CareersPage() {
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchRoles() {
      try {
        const data = await getRoles()
        setRoles(Array.isArray(data) ? data : [])
      } catch (error) {
        console.error("Failed to fetch roles:", error)
        setRoles([])
      } finally {
        setLoading(false)
      }
    }
    fetchRoles()
  }, [])

  if (loading) {
    return <CareersSkeleton />
  }

  return (
    <div className="space-y-12">
      <section className="relative overflow-hidden rounded-3xl border border-border/60 bg-gradient-to-br from-primary/[0.07] via-background to-violet-500/[0.06] px-6 py-12 text-center shadow-sm sm:px-10 sm:py-16">
        <div
          className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -bottom-24 -left-16 h-56 w-56 rounded-full bg-violet-500/10 blur-3xl"
          aria-hidden
        />
        <div className="relative mx-auto max-w-2xl space-y-4">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-background/80 px-3 py-1 text-xs font-medium text-primary backdrop-blur">
            <Sparkles className="h-3.5 w-3.5" />
            We are hiring
          </span>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Build the future of hiring with us
          </h1>
          <p className="text-base text-muted-foreground sm:text-lg leading-relaxed">
            Explore open roles and apply in minutes. We review every profile and get
            back to qualified candidates quickly.
          </p>
        </div>
      </section>

      <section className="space-y-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold tracking-tight sm:text-2xl">
              Open positions
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              {roles.length === 0
                ? "No listings right now — check back soon."
                : `${roles.length} role${roles.length === 1 ? "" : "s"} available`}
            </p>
          </div>
        </div>

        <div className="grid auto-rows-fr gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {roles.map((role) => (
            <article
              key={role.id}
              className="group flex h-full min-h-0 flex-col rounded-2xl border border-border/60 bg-card p-6 shadow-sm transition-all duration-200 hover:border-primary/25 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex min-w-0 items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Briefcase className="h-5 w-5" />
                  </span>
                  <div className="min-w-0">
                    <h3 className="font-semibold leading-snug tracking-tight group-hover:text-primary transition-colors">
                      {role.title}
                    </h3>
                    <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
                      <span className="inline-flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5 shrink-0" />
                        {role.experience_required != null && role.experience_required > 0
                          ? `${role.experience_required}+ yrs`
                          : role.experience_required === 0
                            ? "Entry level"
                            : "Experience TBD"}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 shrink-0" />
                        Remote-friendly
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <p className="mt-4 min-h-[4.125rem] text-sm leading-relaxed text-muted-foreground line-clamp-3 [overflow-wrap:anywhere] break-words">
                {role.description}
              </p>

              {role.required_skills?.length > 0 && (
                <div className="mt-4 flex flex-wrap content-start gap-2">
                  {role.required_skills.slice(0, 5).map((skill, i) => (
                    <span
                      key={i}
                      className="inline-block max-w-full rounded-md border border-border/80 bg-muted/40 px-2 py-1 text-left text-[11px] font-medium leading-snug text-foreground/90 [overflow-wrap:anywhere] break-words sm:max-w-[calc(50%-0.25rem)]"
                    >
                      {skill}
                    </span>
                  ))}
                  {role.required_skills.length > 5 && (
                    <span className="inline-flex items-center self-center text-[11px] text-muted-foreground">
                      +{role.required_skills.length - 5} more
                    </span>
                  )}
                </div>
              )}

              <div className="min-h-0 flex-1" aria-hidden />

              <div className="pt-6">
                <Button className="w-full rounded-xl" asChild>
                  <Link href={`/careers/apply/${role.id}`}>
                    Apply
                    <ArrowRight className="ml-2 h-4 w-4 opacity-80" />
                  </Link>
                </Button>
              </div>
            </article>
          ))}

          {roles.length === 0 && (
            <div className="col-span-full flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 bg-muted/20 px-6 py-16 text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground/50" />
              <p className="mt-4 text-lg font-medium">No open roles yet</p>
              <p className="mt-1 max-w-sm text-sm text-muted-foreground">
                We will post new opportunities here. Follow us or check back later.
              </p>
              <Button variant="outline" className="mt-6 rounded-xl" asChild>
                <Link href="/dashboard" target="_blank" rel="noopener noreferrer">
                  Recruiter console
                </Link>
              </Button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
