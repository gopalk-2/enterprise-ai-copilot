"""
observability/rag_evaluator.py
──────────────────────────────
Continuous RAG Evaluation pipeline using Ragas + local Ollama LLM as judge.
No OpenAI API key required — uses gemma4:31b-cloud for all scoring.

Public API:
    evaluate_rag_sample(question, answer, contexts, ground_truth) -> dict
    run_evaluation_suite(n_samples=10, role="employee") -> dict

Results are appended to data/logs/rag_eval_results.jsonl (one JSON per line).
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("ai_assistant")

# ── Paths ────────────────────────────────────────────────────────────────────
_here       = os.path.dirname(os.path.abspath(__file__))
_EVAL_LOG   = os.path.join(_here, "..", "..", "data", "logs", "rag_eval_results.jsonl")
_GOLDEN_DS  = os.path.join(_here, "..", "..", "data", "eval", "golden_dataset.json")
os.makedirs(os.path.dirname(_EVAL_LOG), exist_ok=True)


# ── Ragas local LLM setup ────────────────────────────────────────────────────

def _build_ragas_llm():
    """
    Wraps the local Ollama LLM for use as the Ragas LLM critic.
    Falls back gracefully if Ragas is not installed.
    """
    try:
        from langchain_ollama import OllamaLLM
        from ragas.llms import LangchainLLMWrapper
        from langchain_community.embeddings import OllamaEmbeddings

        llm        = OllamaLLM(model="gemma4:31b-cloud", temperature=0.0)
        embeddings = OllamaEmbeddings(model="gemma4:31b-cloud")
        return LangchainLLMWrapper(llm), embeddings
    except ImportError as e:
        logger.error(f"[RAG Eval] Ragas not installed or import failed: {e}")
        return None, None


def _build_ragas_embeddings():
    """Separate embeddings wrapper for Ragas embedding-based metrics."""
    try:
        from langchain_community.embeddings import OllamaEmbeddings
        from ragas.embeddings import LangchainEmbeddingsWrapper
        emb = OllamaEmbeddings(model="gemma4:31b-cloud")
        return LangchainEmbeddingsWrapper(emb)
    except ImportError:
        return None


# ── Core evaluator ───────────────────────────────────────────────────────────

def evaluate_rag_sample(
    question:     str,
    answer:       str,
    contexts:     list[str],
    ground_truth: str = "",
) -> dict:
    """
    Evaluate a single RAG sample with Ragas metrics.
    Returns a dict with scores: faithfulness, answer_relevancy, context_precision.
    All scoring uses the local Ollama LLM — no external API required.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision
        from datasets import Dataset

        ragas_llm, _ = _build_ragas_llm()
        ragas_emb     = _build_ragas_embeddings()

        if ragas_llm is None:
            return {"error": "Ragas LLM unavailable", "scores": {}}

        # Build a single-row Ragas dataset
        data = {
            "question":    [question],
            "answer":      [answer],
            "contexts":    [contexts],
            "ground_truth": [ground_truth or ""],
        }
        dataset = Dataset.from_dict(data)

        # Configure metrics with local LLM
        metrics = [faithfulness, answer_relevancy, context_precision]
        for m in metrics:
            m.llm = ragas_llm
            if hasattr(m, "embeddings") and ragas_emb:
                m.embeddings = ragas_emb

        result = evaluate(dataset, metrics=metrics)
        scores = {
            "faithfulness":      round(float(result["faithfulness"]),       3),
            "answer_relevancy":  round(float(result["answer_relevancy"]),   3),
            "context_precision": round(float(result["context_precision"]),  3),
        }
        logger.info(f"[RAG Eval] Sample scored: {json.dumps(scores)}")
        return {"question": question, "scores": scores}

    except Exception as exc:
        logger.error(f"[RAG Eval] evaluate_rag_sample failed: {exc}")
        return {"error": str(exc), "scores": {}}


# ── Evaluation suite ──────────────────────────────────────────────────────────

def run_evaluation_suite(n_samples: int = 10, role: str = "employee") -> dict:
    """
    Run the full evaluation suite over the golden dataset.

    For each Q&A pair:
      1. Run the live RAG pipeline (stream_answer).
      2. Score with Ragas (local Ollama).
      3. Append result to rag_eval_results.jsonl.

    Returns aggregate metrics.
    """
    logger.info(f"[RAG Eval] Starting evaluation suite (n={n_samples}, role={role})")

    # Load golden dataset
    if not os.path.exists(_GOLDEN_DS):
        return {"error": f"Golden dataset not found at {_GOLDEN_DS}"}

    with open(_GOLDEN_DS) as f:
        golden = json.load(f)

    samples    = golden[:n_samples]
    all_scores = []
    run_id     = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for i, item in enumerate(samples):
        question     = item["question"]
        ground_truth = item.get("ground_truth", "")
        logger.info(f"[RAG Eval] [{i+1}/{len(samples)}] Evaluating: {question[:60]}")

        # ── 1. Run live RAG pipeline ─────────────────────────────────────────
        try:
            from rag.query.qa_chain import get_qa_chain
            qa_chain    = get_qa_chain(role)
            rag_result  = qa_chain(question)
            answer      = rag_result.get("result", "")
            source_docs = rag_result.get("source_documents", [])
            contexts    = [doc.page_content for doc in source_docs] or ["(no context retrieved)"]
        except Exception as exc:
            logger.error(f"[RAG Eval] RAG pipeline failed for sample {i}: {exc}")
            answer   = ""
            contexts = ["(pipeline error)"]

        # ── 2. Score with Ragas ──────────────────────────────────────────────
        eval_result = evaluate_rag_sample(question, answer, contexts, ground_truth)
        scores      = eval_result.get("scores", {})

        # ── 3. Persist result ─────────────────────────────────────────────────
        record = {
            "run_id":       run_id,
            "timestamp":    datetime.now(timezone.utc).isoformat(),
            "question":     question,
            "ground_truth": ground_truth,
            "answer":       answer[:500],
            "contexts":     [c[:300] for c in contexts],
            "scores":       scores,
        }
        with open(_EVAL_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")

        if scores:
            all_scores.append(scores)

    # ── Aggregate ─────────────────────────────────────────────────────────────
    if not all_scores:
        return {"run_id": run_id, "error": "No samples were scored successfully."}

    def _avg(key):
        vals = [s[key] for s in all_scores if key in s]
        return round(sum(vals) / len(vals), 3) if vals else None

    aggregate = {
        "run_id":            run_id,
        "n_samples":         len(all_scores),
        "faithfulness":      _avg("faithfulness"),
        "answer_relevancy":  _avg("answer_relevancy"),
        "context_precision": _avg("context_precision"),
        "results_file":      _EVAL_LOG,
    }
    logger.info(f"[RAG Eval] Suite complete: {json.dumps(aggregate)}")
    return aggregate


# ── Read past results ─────────────────────────────────────────────────────────

def get_eval_results(last_n: int = 20) -> list[dict]:
    """Read the last N evaluation records from the JSONL log."""
    if not os.path.exists(_EVAL_LOG):
        return []
    try:
        with open(_EVAL_LOG) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        return lines[-last_n:]
    except Exception as exc:
        logger.error(f"[RAG Eval] Failed to read results: {exc}")
        return []
