"""
Evaluation script — So sánh A/B giữa dense-only và hybrid + RRF.

Chạy: python -m src.evaluate
"""

import json
import time
from pathlib import Path

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task10_generation import (
    SYSTEM_PROMPT,
    call_llm,
    format_context,
    reorder_for_llm,
)


GOLDEN_PATH = Path(__file__).parent.parent / "group_project" / "evaluation" / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent.parent / "group_project" / "evaluation"


def load_golden_dataset() -> list[dict]:
    """Load golden dataset từ file JSON."""
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    return data


def run_config_a(query: str, top_k: int = 5) -> dict:
    """Config A: Dense-only (không dùng RRF)."""
    dense = semantic_search(query, top_k=top_k)
    return {
        "chunks": dense[:top_k],
        "retrieval_source": "hybrid",  # label for consistency
        "config": "A (dense-only)",
    }


def run_config_b(query: str, top_k: int = 5) -> dict:
    """Config B: Hybrid + RRF (dense + BM25 fused)."""
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)
    hybrid = rerank_rrf([dense, sparse], top_k=top_k)
    return {
        "chunks": hybrid,
        "retrieval_source": "hybrid",
        "config": "B (hybrid + RRF)",
    }


def generate_answer(chunks: list[dict], query: str) -> str:
    """Generate an answer from retrieved chunks."""
    if not chunks:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        return call_llm(SYSTEM_PROMPT, user_message)
    except Exception as e:
        return f"[LLM Error: {e}]"


def evaluate_single(
    question: str,
    expected_answer: str,
    expected_context: str,
    generated_answer: str,
    retrieved_chunks: list[dict],
) -> dict:
    """Evaluate a single case using LLM-as-judge for 4 metrics."""
    context_text = "\n".join(c["content"] for c in retrieved_chunks) if retrieved_chunks else ""

    eval_prompt = f"""Bạn là evaluator cho hệ thống RAG. Đánh giá câu trả lời dựa trên 4 tiêu chí.
Cho điểm mỗi tiêu chí từ 0.0 đến 1.0.

Câu hỏi: {question}
Câu trả lời mong đợi: {expected_answer}
Context mong đợi: {expected_context}
Câu trả lời hệ thống: {generated_answer}
Context đã truy xuất: {context_text[:2000]}

Trả lời CHÍNH XÁC theo format JSON (không markdown):
{{"faithfulness": 0.0, "answer_relevance": 0.0, "context_recall": 0.0, "context_precision": 0.0}}

Giải thích ngắn:
- faithfulness: Câu trả lời có bám sát context không?
- answer_relevance: Câu trả lời có giải quyết câu hỏi không?
- context_recall: Context có chứa thông tin cần thiết không?
- context_precision: Context có tập trung hay chứa nhiều nhiễu không?"""

    try:
        result_text = call_llm("Bạn là evaluator. Chỉ trả về JSON.", eval_prompt)
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[^}]+\}', result_text)
        if json_match:
            scores = json.loads(json_match.group())
            return {
                "faithfulness": float(scores.get("faithfulness", 0)),
                "answer_relevance": float(scores.get("answer_relevance", 0)),
                "context_recall": float(scores.get("context_recall", 0)),
                "context_precision": float(scores.get("context_precision", 0)),
            }
    except Exception as e:
        print(f"  Evaluation error: {e}")

    return {
        "faithfulness": 0.0,
        "answer_relevance": 0.0,
        "context_recall": 0.0,
        "context_precision": 0.0,
    }


def run_evaluation(top_k: int = 5):
    """Run full A/B evaluation."""
    dataset = load_golden_dataset()
    print(f"Loaded {len(dataset)} golden cases")

    results_a = []
    results_b = []

    for i, case in enumerate(dataset):
        question = case["question"]
        expected_answer = case["expected_answer"]
        expected_context = case["expected_context"]

        print(f"\n--- Case {i+1}/{len(dataset)}: {question[:60]}... ---")

        # Config A: Dense-only
        print("  Running Config A (dense-only)...")
        config_a = run_config_a(question, top_k)
        answer_a = generate_answer(config_a["chunks"], question)
        time.sleep(1)  # Rate limiting
        scores_a = evaluate_single(
            question, expected_answer, expected_context,
            answer_a, config_a["chunks"]
        )
        results_a.append({
            "question": question,
            "answer": answer_a,
            "scores": scores_a,
            "num_chunks": len(config_a["chunks"]),
        })
        print(f"  Config A scores: {scores_a}")

        # Config B: Hybrid + RRF
        print("  Running Config B (hybrid + RRF)...")
        config_b = run_config_b(question, top_k)
        answer_b = generate_answer(config_b["chunks"], question)
        time.sleep(1)  # Rate limiting
        scores_b = evaluate_single(
            question, expected_answer, expected_context,
            answer_b, config_b["chunks"]
        )
        results_b.append({
            "question": question,
            "answer": answer_b,
            "scores": scores_b,
            "num_chunks": len(config_b["chunks"]),
        })
        print(f"  Config B scores: {scores_b}")

    # Compute averages
    metrics = ["faithfulness", "answer_relevance", "context_recall", "context_precision"]
    avg_a = {m: sum(r["scores"][m] for r in results_a) / len(results_a) for m in metrics}
    avg_b = {m: sum(r["scores"][m] for r in results_b) / len(results_b) for m in metrics}
    delta = {m: avg_b[m] - avg_a[m] for m in metrics}

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"\n{'Metric':<20} {'Config A':>10} {'Config B':>10} {'Delta':>10}")
    print("-" * 50)
    for m in metrics:
        print(f"{m:<20} {avg_a[m]:>10.3f} {avg_b[m]:>10.3f} {delta[m]:>+10.3f}")

    overall_a = sum(avg_a.values()) / 4
    overall_b = sum(avg_b.values()) / 4
    overall_delta = overall_b - overall_a
    print(f"{'Average':<20} {overall_a:>10.3f} {overall_b:>10.3f} {overall_delta:>+10.3f}")

    # Save detailed results
    output = {
        "config_a": results_a,
        "config_b": results_b,
        "averages": {"config_a": avg_a, "config_b": avg_b, "delta": delta},
    }
    output_path = RESULTS_PATH / "evaluation_results.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDetailed results saved to: {output_path}")

    # Find worst performers
    all_cases = []
    for i in range(len(dataset)):
        for config_name, results in [("A", results_a), ("B", results_b)]:
            r = results[i]
            avg_score = sum(r["scores"].values()) / 4
            all_cases.append({
                "index": i + 1,
                "question": r["question"],
                "config": config_name,
                "scores": r["scores"],
                "avg_score": avg_score,
            })

    worst = sorted(all_cases, key=lambda x: x["avg_score"])[:3]
    print("\nWorst performers:")
    for w in worst:
        print(f"  Case {w['index']} (Config {w['config']}): avg={w['avg_score']:.3f} - {w['question'][:50]}")

    return output


if __name__ == "__main__":
    run_evaluation()
