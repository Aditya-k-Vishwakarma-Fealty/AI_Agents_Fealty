"use client"

import { useCallback, useMemo, useState } from "react"
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
} from "@dnd-kit/core"
import Link from "next/link"
import { updateCandidateStage } from "@/api/candidates"
import {
  formatStage,
  formatStatus,
  statusBadgeClass,
} from "@/lib/hr-format"
import { cn } from "@/lib/utils"
import { GripVertical } from "lucide-react"

export const PIPELINE_STAGES = [
  "submitted",
  "parsed",
  "scored",
  "shortlisted",
  "interviewed",
  "final",
]

function DraggableCard({ candidate }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({
      id: `cand-${candidate.id}`,
      data: { candidate },
    })

  const style = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)` }
    : undefined

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "rounded-lg border border-border/60 bg-background p-3 shadow-sm transition-shadow",
        isDragging && "opacity-30"
      )}
    >
      <div className="flex items-start gap-2">
        <button
          type="button"
          className="mt-0.5 cursor-grab touch-none text-muted-foreground hover:text-foreground active:cursor-grabbing"
          aria-label="Drag to change stage"
          {...listeners}
          {...attributes}
        >
          <GripVertical className="h-4 w-4" />
        </button>
        <div className="min-w-0 flex-1">
          <Link
            href={`/candidates/${candidate.id}`}
            className="text-sm font-medium hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            {candidate.name}
          </Link>
          <p className="truncate text-xs text-muted-foreground">{candidate.email}</p>
          <div className="mt-2 flex flex-wrap gap-1">
            <span
              className={cn(
                "inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium ring-1 ring-inset",
                statusBadgeClass(candidate.status)
              )}
            >
              {formatStatus(candidate.status)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

function StageColumn({ stage, candidates }) {
  const { setNodeRef, isOver } = useDroppable({ id: `stage-${stage}` })

  return (
    <div className="flex w-[min(100%,260px)] shrink-0 flex-col rounded-xl border border-border/60 bg-muted/15">
      <div className="border-b border-border/60 px-3 py-2.5">
        <p className="text-sm font-semibold">{formatStage(stage)}</p>
        <p className="text-[11px] text-muted-foreground">
          {candidates.length} candidate{candidates.length === 1 ? "" : "s"}
        </p>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          "flex min-h-[220px] flex-1 flex-col gap-2 p-2",
          isOver && "bg-primary/5"
        )}
      >
        {candidates.map((c) => (
          <DraggableCard key={c.id} candidate={c} />
        ))}
        {candidates.length === 0 && (
          <p className="py-10 text-center text-xs text-muted-foreground">
            Drop candidates here
          </p>
        )}
      </div>
    </div>
  )
}

export function PipelineBoard({ initialCandidates }) {
  const [candidates, setCandidates] = useState(() =>
    Array.isArray(initialCandidates) ? initialCandidates : []
  )
  const [activeId, setActiveId] = useState(null)

  const findCandidate = useCallback(
    (id) => candidates.find((c) => c.id === id),
    [candidates]
  )

  const byStage = useMemo(() => {
    const m = {}
    for (const s of PIPELINE_STAGES) m[s] = []
    for (const c of candidates) {
      const st = String(c.current_stage || "submitted").toLowerCase()
      if (m[st]) m[st].push(c)
      else m.submitted.push(c)
    }
    return m
  }, [candidates])

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 10 } })
  )

  const resolveTargetStage = useCallback(
    (overId) => {
      const s = String(overId)
      if (s.startsWith("stage-")) return s.replace("stage-", "")
      if (s.startsWith("cand-")) {
        const cid = parseInt(s.replace("cand-", ""), 10)
        const c = findCandidate(cid)
        return c ? String(c.current_stage || "").toLowerCase() : null
      }
      return null
    },
    [findCandidate]
  )

  const handleDragEnd = async (event) => {
    const { active, over } = event
    setActiveId(null)
    if (!over) return
    const aid = String(active.id)
    if (!aid.startsWith("cand-")) return
    const candidateId = parseInt(aid.replace("cand-", ""), 10)
    const targetStage = resolveTargetStage(over.id)
    if (!targetStage) return
    const cand = findCandidate(candidateId)
    if (!cand || String(cand.current_stage || "").toLowerCase() === targetStage) {
      return
    }

    const snapshot = candidates
    setCandidates((prev) =>
      prev.map((c) =>
        c.id === candidateId ? { ...c, current_stage: targetStage } : c
      )
    )
    try {
      await updateCandidateStage(candidateId, targetStage)
    } catch (e) {
      console.error(e)
      setCandidates(snapshot)
      alert("Could not update stage. Try again.")
    }
  }

  const activeDrag = activeId
    ? findCandidate(parseInt(String(activeId).replace("cand-", ""), 10))
    : null

  return (
    <DndContext
      sensors={sensors}
      onDragStart={(e) => setActiveId(String(e.active.id))}
      onDragEnd={handleDragEnd}
      onDragCancel={() => setActiveId(null)}
    >
      <div className="flex gap-4 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:thin]">
        {PIPELINE_STAGES.map((stage) => (
          <StageColumn
            key={stage}
            stage={stage}
            candidates={byStage[stage] || []}
          />
        ))}
      </div>
      <DragOverlay dropAnimation={null}>
        {activeDrag ? (
          <div className="w-[240px] rounded-lg border border-border bg-background p-3 shadow-xl">
            <p className="text-sm font-medium">{activeDrag.name}</p>
            <p className="text-xs text-muted-foreground">
              {formatStage(activeDrag.current_stage)}
            </p>
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}
