"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Bạn là trợ lý hỏi đáp về tuyển sinh đại học Việt Nam.
Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải trích dẫn nguồn bằng cách ghi [Document N] tương ứng.
Nếu context không chứa đủ thông tin để trả lời, hãy nói rõ rằng bạn không tìm thấy
đủ bằng chứng trong nguồn hiện có và từ chối xác minh.
Trả lời bằng tiếng Việt."""


SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context.

    Sử dụng chiến lược lost-in-the-middle: chunks quan trọng nhất
    (score cao nhất) được đặt ở đầu và cuối danh sách, tránh bị
    kẹt giữa context nơi LLM dễ bỏ qua.
    """
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]   # even indices (0, 2, 4, ...) → đầu
    back = chunks[1::2]   # odd indices (1, 3, ...) → cuối, đảo ngược
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label để LLM tạo citation kiểm chứng được."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[Document {index} | Title: {metadata['title']} | "
            f"Source: {metadata['source']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình.

    Dispatch theo LLM_PROVIDER trong .env. Trả về text thuần.
    """
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower().strip()

    if provider in ("local", "extractive"):
        # Local heuristic synthesizer for offline / zero-key testing
        lines = [p.strip() for p in user_message.split("\n\n---\n\n") if p.strip()]
        answer_parts = []
        for i, part in enumerate(lines, 1):
            doc_label = f"[Document {i}]"
            text_lines = [
                line.strip()
                for line in part.split("\n")
                if line.strip() and not line.startswith("[Document") and not line.startswith("Context:") and not line.startswith("Question:")
            ]
            if text_lines:
                summary_snippet = " ".join(text_lines[:2])
                if len(summary_snippet) > 280:
                    summary_snippet = summary_snippet[:277] + "..."
                answer_parts.append(f"- Căn cứ theo {doc_label}: {summary_snippet}")

        if answer_parts:
            return "Dựa trên các tài liệu quy chế và thông tin tuyển sinh chính thức:\n\n" + "\n\n".join(answer_parts)
        return SAFE_REFUSAL

    elif provider == "gemini":
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not configured in .env")

        client = genai.Client(api_key=api_key)
        model = os.getenv("LLM_MODEL", LLM_MODEL) or "gemini-2.0-flash"

        response = client.models.generate_content(
            model=model,
            contents=f"{system_prompt}\n\n{user_message}",
            config=genai.types.GenerateContentConfig(
                temperature=TEMPERATURE,
                top_p=TOP_P,
            ),
        )
        return response.text

    elif provider in ("openai", "9router"):
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", None)
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not configured in .env")

        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        model = os.getenv("LLM_MODEL", LLM_MODEL) or "ag/gemini-3.8-flash"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not configured in .env")

        client = anthropic.Anthropic(api_key=api_key)
        model = os.getenv("LLM_MODEL", LLM_MODEL) or "claude-sonnet-4-20250514"

        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.content[0].text

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult với answer, sources và retrieval_source.

    Khi không có chunk hoặc LLM lỗi, trả safe refusal thay vì crash.
    """
    chunks = retrieve(query, top_k=top_k)

    if not chunks:
        return {
            "answer": SAFE_REFUSAL,
            "sources": [],
            "retrieval_source": "none",
        }

    # Xác định retrieval_source từ method của chunks đã trả về
    first_method = chunks[0].get("retrieval_method", "hybrid")
    if first_method == "pageindex":
        retrieval_source = "pageindex"
    else:
        retrieval_source = "hybrid"

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as e:
        # LLM lỗi → safe refusal, không crash
        answer = f"{SAFE_REFUSAL} (Lỗi hệ thống: {type(e).__name__})"
        return {
            "answer": answer,
            "sources": chunks,
            "retrieval_source": retrieval_source,
        }

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("test query"))
