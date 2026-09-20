"""Run a reproducible dense-only versus hybrid-RRF evaluation.

The script intentionally keeps the corpus, top_k, LLM model and evaluation
prompt fixed.  It writes one artifact per run so the aggregate report can be
traced back to each golden case.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from src.task10_generation import call_llm, format_context, reorder_for_llm
from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank_rrf


ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = ROOT / "group_project" / "evaluation" / "golden_dataset.json"
OUTPUT_PATH = ROOT / "group_project" / "evaluation" / "ab_results.json"
TOP_K = 5
RRF_K = 60

SYSTEM_PROMPT = """You are a strict Vietnamese RAG evaluator.
Use only the retrieved context. Return one JSON object and no Markdown with:
answer (a concise Vietnamese answer with [Document N] citations),
faithfulness, answer_relevance, context_recall, context_precision (numbers in
[0, 1]), and rationale (one concise sentence). Faithfulness rates whether the
answer is supported by retrieved context. Answer relevance rates whether it
answers the question. Context recall rates whether retrieved context contains
the expected evidence. Context precision rates how focused retrieved chunks
are on that evidence. Do not infer facts outside the context."""


def _git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def _json_response(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"LLM did not return JSON: {text[:300]!r}")
    payload = json.loads(match.group())
    for key in ("answer", "faithfulness", "answer_relevance", "context_recall", "context_precision"):
        if key not in payload:
            raise ValueError(f"LLM response is missing {key}")
    for key in ("faithfulness", "answer_relevance", "context_recall", "context_precision"):
        payload[key] = max(0.0, min(1.0, float(payload[key])))
    if not isinstance(payload["answer"], str) or not payload["answer"].strip():
        raise ValueError("LLM returned an empty answer")
    return payload


def _evaluate_with_provider(prompt: str) -> dict:
    """Use the configured provider for both fixed configurations."""
    return _json_response(call_llm(SYSTEM_PROMPT, prompt))


def _retrieve(question: str, configuration: str) -> tuple[list[dict], float]:
    started = time.perf_counter()
    dense = semantic_search(question, top_k=TOP_K * 2)
    if configuration == "dense-only":
        results = dense[:TOP_K]
    else:
        sparse = lexical_search(question, top_k=TOP_K * 2)
        results = rerank_rrf([dense, sparse], top_k=TOP_K, k=RRF_K)
    return results, time.perf_counter() - started


def _case_prompt(case: dict, chunks: list[dict]) -> str:
    context = format_context(reorder_for_llm(chunks))
    return (
        f"Question: {case['question']}\n"
        f"Expected answer: {case['expected_answer']}\n"
        f"Expected evidence: {case['expected_context']}\n\n"
        f"Retrieved context:\n{context}"
    )


def run() -> dict:
    load_dotenv(ROOT / ".env")
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if len(golden) < 15:
        raise ValueError("golden dataset must contain at least 15 cases")

    if OUTPUT_PATH.exists():
        payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        records: list[dict] = payload.get("records", [])
    else:
        payload = {
            "run_at": datetime.now(UTC).isoformat(),
            "corpus_commit": _git_commit(),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
            "llm_provider": os.getenv("LLM_PROVIDER", "").strip().lower(),
            "generator_evaluator_model": (
                os.getenv("DEEPSEEK_MODEL", "").strip()
                if os.getenv("LLM_PROVIDER", "").strip().lower() == "deepseek"
                else os.getenv("LLM_MODEL", "").strip() or "provider default"
            ),
            "top_k": TOP_K,
            "rrf_k": RRF_K,
            "score_threshold": 0.3,
            "records": records,
        }

    selected = os.getenv("EVALUATION_CONFIGURATION", "all").strip().lower()
    configurations = ("dense-only", "hybrid-rrf") if selected == "all" else (selected,)
    if any(item not in {"dense-only", "hybrid-rrf"} for item in configurations):
        raise ValueError("EVALUATION_CONFIGURATION must be all, dense-only, or hybrid-rrf")
    max_cases = int(os.getenv("EVALUATION_MAX_CASES", "0"))
    completed = 0
    existing = {(item["configuration"], item["case"]) for item in records}

    for configuration in configurations:
        for index, case in enumerate(golden, start=1):
            if (configuration, index) in existing:
                continue
            if max_cases and completed >= max_cases:
                return payload
            chunks, retrieval_seconds = _retrieve(case["question"], configuration)
            if not chunks:
                raise RuntimeError(f"{configuration} returned no chunks for case {index}")
            generated = _evaluate_with_provider(_case_prompt(case, chunks))
            records.append(
                {
                    "case": index,
                    "configuration": configuration,
                    "question": case["question"],
                    "expected_answer": case["expected_answer"],
                    "expected_context": case["expected_context"],
                    "answer": generated["answer"],
                    "faithfulness": generated["faithfulness"],
                    "answer_relevance": generated["answer_relevance"],
                    "context_recall": generated["context_recall"],
                    "context_precision": generated["context_precision"],
                    "rationale": generated.get("rationale", ""),
                    "retrieval_seconds": round(retrieval_seconds, 4),
                    "sources": [chunk["id"] for chunk in chunks],
                }
            )
            payload["records"] = records
            OUTPUT_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            completed += 1
            print(f"{configuration}: case {index}/{len(golden)} complete", flush=True)

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")
    return payload


if __name__ == "__main__":
    run()
