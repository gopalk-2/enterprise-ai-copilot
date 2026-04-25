"""
api/eval_router.py
──────────────────
Admin-only FastAPI router for RAG evaluation.

Endpoints:
    POST /eval/run      — Trigger an evaluation suite run (async background task)
    GET  /eval/results  — Retrieve last N evaluation records
    GET  /eval/status   — Check if a run is currently in progress
"""

import threading
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from security.auth.dependencies import get_current_user

router = APIRouter(prefix="/eval", tags=["evaluation"])

# ── In-memory run state (lightweight — no persistence needed) ─────────────────
_run_state: dict = {
    "running":    False,
    "run_id":     None,
    "started_at": None,
    "result":     None,
    "error":      None,
}


class EvalRunRequest(BaseModel):
    n_samples: int = 10
    role: str = "employee"


def _require_admin(user=Depends(get_current_user)):
    """FastAPI dependency: reject non-admin users."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for evaluation endpoints.")
    return user


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/run")
def trigger_eval_run(
    request: EvalRunRequest,
    user=Depends(_require_admin),
):
    """
    Triggers a RAG evaluation suite in a background thread.
    Returns immediately with a run_id.
    """
    global _run_state

    if _run_state["running"]:
        return {
            "status":  "already_running",
            "run_id":  _run_state["run_id"],
            "message": "An evaluation is already in progress. Check /eval/status.",
        }

    def _run():
        global _run_state
        _run_state["running"]    = True
        _run_state["result"]     = None
        _run_state["error"]      = None
        _run_state["started_at"] = time.time()
        try:
            from observability.rag_evaluator import run_evaluation_suite
            result = run_evaluation_suite(
                n_samples=request.n_samples,
                role=request.role,
            )
            _run_state["result"] = result
            _run_state["run_id"] = result.get("run_id")
        except Exception as exc:
            _run_state["error"] = str(exc)
        finally:
            _run_state["running"] = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return {
        "status":  "started",
        "message": f"Evaluation suite started with {request.n_samples} samples (role={request.role}).",
        "hint":    "Poll GET /eval/status to check progress, GET /eval/results for past results.",
    }


@router.get("/status")
def eval_status(user=Depends(_require_admin)):
    """Return current evaluation run state."""
    elapsed = None
    if _run_state["running"] and _run_state["started_at"]:
        elapsed = round(time.time() - _run_state["started_at"], 1)

    return {
        "running":    _run_state["running"],
        "run_id":     _run_state["run_id"],
        "elapsed_s":  elapsed,
        "last_result": _run_state["result"],
        "last_error":  _run_state["error"],
    }


@router.get("/results")
def get_eval_results(
    last_n: int = Query(default=20, ge=1, le=100),
    user=Depends(_require_admin),
):
    """
    Returns the last N evaluation records from the persistent JSONL log.
    Each record contains question, answer, contexts, and Ragas scores.
    """
    from observability.rag_evaluator import get_eval_results
    records = get_eval_results(last_n=last_n)
    return {
        "count":   len(records),
        "records": records,
    }
