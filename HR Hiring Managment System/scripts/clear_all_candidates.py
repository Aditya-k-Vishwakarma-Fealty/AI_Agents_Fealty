#!/usr/bin/env python3
"""
Delete all applicants (candidates) and related rows from the database.
Also removes resume files from disk when paths are known.

Usage (from repo root of this service):
  cd "HR Hiring Managment System"
  ./venv/bin/python scripts/clear_all_candidates.py

Roles are NOT deleted.
"""
from __future__ import annotations

import os
import sys

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.db.models import (
    Candidate,
    CandidateScore,
    EmailLog,
    FinalRanking,
    Interview,
)


def main() -> None:
    db = SessionLocal()
    try:
        rows = db.execute(select(Candidate.id, Candidate.resume_path)).all()
        candidate_ids = [r[0] for r in rows]
        removed = 0
        for _, p in rows:
            if p and os.path.isfile(p):
                try:
                    os.remove(p)
                    removed += 1
                except OSError as e:
                    print(f"Warning: could not delete file {p}: {e}", file=sys.stderr)

        db.execute(delete(EmailLog))
        db.execute(delete(FinalRanking))
        db.execute(delete(Interview))
        db.execute(delete(CandidateScore))
        db.execute(delete(Candidate))
        db.commit()

        chroma_removed = 0
        try:
            from app.vectorstore.chroma_client import chroma_client

            for cid in candidate_ids:
                try:
                    chroma_client.delete_resume(cid)
                    chroma_removed += 1
                except Exception as e:
                    print(f"Warning: Chroma resume_{cid}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Chroma cleanup skipped: {e}", file=sys.stderr)

        print(f"OK: Removed all candidates and related records (scores, interviews, rankings, email logs).")
        print(f"OK: Deleted {removed} resume file(s) from disk.")
        if chroma_removed:
            print(f"OK: Removed {chroma_removed} resume embedding(s) from ChromaDB.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
