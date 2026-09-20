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

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation dạng [Document N]. Nếu thiếu evidence,
hãy từ chối xác minh."""
SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[Document {index} | Title: {metadata['title']} | "
            f"Source: {metadata['source']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).strip().lower()
    model = os.getenv("LLM_MODEL", LLM_MODEL).strip()

    if provider == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        response = OpenAI(api_key=api_key).chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return (response.choices[0].message.content or "").strip()

    if provider == "deepseek":
        from openai import OpenAI

        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")
        response = OpenAI(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
        ).chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "").strip() or model or "deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return (response.choices[0].message.content or "").replace(
            "<|endoftext|>", ""
        ).strip()

    if provider == "gemini":
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        response = genai.Client(api_key=api_key).models.generate_content(
            model=model or "gemini-2.0-flash",
            contents=f"{system_prompt}\n\n{user_message}",
        )
        return (getattr(response, "text", None) or "").strip()

    if provider == "anthropic":
        from anthropic import Anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        response = Anthropic(api_key=api_key).messages.create(
            model=model or "claude-3-5-haiku-latest",
            max_tokens=1024,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        ).strip()

    raise ValueError("LLM_PROVIDER must be openai, deepseek, gemini, or anthropic")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}

    context = format_context(reorder_for_llm(chunks))
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}

    if not answer:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    retrieval_source = (
        "pageindex" if chunks[0]["retrieval_method"] == "pageindex" else "hybrid"
    )
    return {"answer": answer, "sources": chunks, "retrieval_source": retrieval_source}


if __name__ == "__main__":
    print(generate_with_citation("test query"))
