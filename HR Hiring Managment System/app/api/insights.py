"""
Recruiter insights — stalled pipeline, aggregated skill gaps, recommended actions.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import (
    Candidate,
    CandidateScore,
    CandidateStage,
    CandidateStatus,
    Interview,
    Role,
)

router = APIRouter(prefix="/insights", tags=["insights"])

STALL_DAYS = 7


def _normalize_gap_item(item: Any) -> str | None:
    if isinstance(item, str) and item.strip():
        return item.strip()
    return None


@router.get("")
async def get_recruiter_insights(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    AI-style operational insights derived from DB signals (no external LLM call).
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=STALL_DAYS)

    stalled_rows = (
        db.query(Candidate)
        .filter(Candidate.status == CandidateStatus.ACTIVE)
        .filter(
            Candidate.current_stage.notin_(
                [CandidateStage.INTERVIEWED, CandidateStage.FINAL]
            )
        )
        .filter(Candidate.application_date <= cutoff)
        .order_by(Candidate.application_date.asc())
        .limit(25)
        .all()
    )

    stalled_candidates: List[Dict[str, Any]] = []
    for c in stalled_rows:
        days = (now - c.application_date).days if c.application_date else 0
        stalled_candidates.append(
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "stage": c.current_stage.value,
                "days_in_pipeline": days,
                "application_date": c.application_date.isoformat()
                if c.application_date
                else None,
            }
        )

    scores_rows = (
        db.query(CandidateScore).filter(CandidateScore.gaps.isnot(None)).all()
    )
    gap_counter: Counter[str] = Counter()
    for s in scores_rows:
        g = s.gaps
        if isinstance(g, list):
            for item in g:
                label = _normalize_gap_item(item)
                if label:
                    gap_counter[label.lower()] += 1
        else:
            label = _normalize_gap_item(g)
            if label:
                gap_counter[label.lower()] += 1

    gap_insights = [
        {"label": k.title(), "count": v} for k, v in gap_counter.most_common(12)
    ]

    stage_rows = (
        db.query(Candidate.current_stage, func.count(Candidate.id))
        .group_by(Candidate.current_stage)
        .all()
    )
    stage_counts: Dict[str, int] = {}
    for st, cnt in stage_rows:
        key = st.value if hasattr(st, "value") else str(st)
        stage_counts[key] = int(cnt or 0)

    scored_waiting = int(stage_counts.get(CandidateStage.SCORED.value, 0) or 0)
    shortlisted_count = int(
        stage_counts.get(CandidateStage.SHORTLISTED.value, 0) or 0
    )
    active_roles = (
        db.query(func.count(Role.id)).filter(Role.is_active.is_(True)).scalar() or 0
    )
    interviews_count = db.query(func.count(Interview.id)).scalar() or 0

    recommended_actions: List[Dict[str, Any]] = []

    if stalled_candidates:
        recommended_actions.append(
            {
                "title": "Unblock stalled candidates",
                "detail": f"{len(stalled_candidates)} active candidates have not progressed in {STALL_DAYS}+ days.",
                "severity": "warning",
                "href": "/pipeline",
            }
        )

    if scored_waiting >= 3 and active_roles > 0:
        recommended_actions.append(
            {
                "title": "Run shortlisting on open roles",
                "detail": f"{scored_waiting} candidates are still in the scored stage.",
                "severity": "info",
                "href": "/roles",
            }
        )

    if shortlisted_count >= 2:
        recommended_actions.append(
            {
                "title": "Schedule interviews for shortlisted talent",
                "detail": f"{shortlisted_count} candidates are shortlisted.",
                "severity": "info",
                "href": "/interviews/schedule",
            }
        )

    if gap_insights:
        top = gap_insights[0]
        recommended_actions.append(
            {
                "title": "Address recurring skill gaps",
                "detail": f"Most frequent gap: {top['label']} ({top['count']} mentions).",
                "severity": "info",
                "href": "/roles",
            }
        )

    if interviews_count == 0 and int(stage_counts.get(CandidateStage.SCORED.value, 0) or 0) > 0:
        recommended_actions.append(
            {
                "title": "Start capturing interview feedback",
                "detail": "You have scored candidates but no interview records yet.",
                "severity": "info",
                "href": "/interviews",
            }
        )

    summary_parts: List[str] = []
    if stalled_candidates:
        summary_parts.append(
            f"{len(stalled_candidates)} candidates need attention in the pipeline."
        )
    else:
        summary_parts.append(
            "No long-stalled active candidates in early/mid stages."
        )
    if gap_insights:
        summary_parts.append(f"Top gap theme: {gap_insights[0]['label']}.")

    return {
        "stall_days": STALL_DAYS,
        "stalled_candidates": stalled_candidates,
        "gap_insights": gap_insights,
        "recommended_actions": recommended_actions[:10],
        "summary": " ".join(summary_parts),
        "stage_counts": stage_counts,
    }
