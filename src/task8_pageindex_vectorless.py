"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Cache for uploaded document IDs
_uploaded_doc_ids: list[str] = []
_client = None


def _get_client():
    """Get or create PageIndex client."""
    global _client
    if _client is None and PAGEINDEX_API_KEY:
        try:
            import pageindex
            _client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
        except Exception:
            _client = None
    return _client


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    global _uploaded_doc_ids

    client = _get_client()
    if client is None:
        print("PageIndex API key not configured or client unavailable. Skipping upload.")
        return

    if _uploaded_doc_ids:
        print(f"Already uploaded {len(_uploaded_doc_ids)} documents")
        return

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
            if len(content.strip()) < 100:
                continue

            # Try uploading as text
            response = client.upload(
                content=content,
                filename=path.name,
            )
            if hasattr(response, "id"):
                _uploaded_doc_ids.append(response.id)
                print(f"Uploaded: {path.name} -> {response.id}")
            elif isinstance(response, dict) and "id" in response:
                _uploaded_doc_ids.append(response["id"])
                print(f"Uploaded: {path.name} -> {response['id']}")
        except Exception as e:
            print(f"Failed to upload {path.name}: {e}")

    print(f"Uploaded {len(_uploaded_doc_ids)} documents to PageIndex")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    client = _get_client()
    if client is None:
        raise RuntimeError("PageIndex API key not configured")

    if not _uploaded_doc_ids:
        upload_documents()

    if not _uploaded_doc_ids:
        raise RuntimeError("No documents uploaded to PageIndex")

    try:
        response = client.search(
            query=query,
            document_ids=_uploaded_doc_ids,
            top_k=top_k,
        )

        results = []
        nodes = response if isinstance(response, list) else getattr(response, "results", [])

        for rank, node in enumerate(nodes[:top_k]):
            # Extract fields — adapt to actual PageIndex response format
            content = getattr(node, "text", "") or getattr(node, "content", "") or str(node)
            score = getattr(node, "score", None) or (top_k - rank) / top_k
            source = getattr(node, "source", "pageindex")
            title = getattr(node, "title", "pageindex_result")

            results.append({
                "id": f"pageindex-{rank}",
                "content": content,
                "score": float(score),
                "metadata": {
                    "source": str(source),
                    "title": str(title),
                    "doc_type": "legal",
                    "url": None,
                    "chunk_index": rank,
                },
                "retrieval_method": "pageindex",
            })

        return sorted(results, key=lambda x: x["score"], reverse=True)

    except Exception as e:
        raise RuntimeError(f"PageIndex search failed: {e}")


if __name__ == "__main__":
    upload_documents()
