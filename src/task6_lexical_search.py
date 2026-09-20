"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import numpy as np
from rank_bm25 import BM25Okapi

from .task4_chunking_indexing import chunk_documents, load_documents


CORPUS: list[dict] = []

_bm25_index = None


def _ensure_corpus():
    """Load corpus if not already loaded."""
    global CORPUS, _bm25_index
    if not CORPUS:
        documents = load_documents()
        CORPUS = chunk_documents(documents)
        _bm25_index = None


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    global _bm25_index
    if _bm25_index is None or getattr(build_bm25_index, "_last_corpus", None) is not corpus:
        tokenized = [item["content"].lower().split() for item in corpus]
        _bm25_index = BM25Okapi(tokenized)
        build_bm25_index._last_corpus = corpus
    return _bm25_index


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    _ensure_corpus()

    if not CORPUS:
        return []

    bm25 = build_bm25_index(CORPUS)
    q_tokens = query.lower().split()
    raw_scores = bm25.get_scores(q_tokens)
    scores = np.array(raw_scores, dtype=float)

    # Handle zero-IDF edge case when corpus is very small (e.g. N=2)
    for i, item in enumerate(CORPUS):
        doc_words = item["content"].lower().split()
        overlap_count = sum(doc_words.count(w) for w in q_tokens)
        if scores[i] <= 0 and overlap_count > 0:
            scores[i] = float(overlap_count)

    indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for index in indices:
        if scores[index] <= 0:
            continue
        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })

    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
