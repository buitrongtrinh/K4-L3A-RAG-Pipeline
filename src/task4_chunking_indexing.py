"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

# Cache the model to avoid reloading
_embedding_model = None


def _get_embedding_model():
    """Get or create the embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts using the configured provider."""
    if not texts:
        return []
    model = _get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=len(texts) > 10)
    return embeddings.tolist()


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []

    if not STANDARDIZED_DIR.exists():
        print(f"Warning: {STANDARDIZED_DIR} does not exist")
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            continue

        # Determine doc_type from path
        relative = path.relative_to(STANDARDIZED_DIR)
        parts = relative.parts
        doc_type = "legal" if "legal" in parts else "news"

        # Extract title from first heading or filename
        title = path.stem
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract URL from metadata if present
        url = None
        for line in content.split("\n"):
            if line.startswith("**Source:**"):
                url_text = line.replace("**Source:**", "").strip()
                if url_text.startswith("http"):
                    url = url_text
                break

        documents.append({
            "id": relative.as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })

    print(f"Loaded {len(documents)} documents")
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for document in documents:
        texts = splitter.split_text(document["content"])
        for index, text in enumerate(texts):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": index},
            })

    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return chunks

    # Embed in batches to manage memory
    batch_size = 32
    all_texts = [chunk["content"] for chunk in chunks]

    print(f"Embedding {len(all_texts)} chunks...")
    vectors = embed_texts(all_texts)

    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector

    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return

    collection = get_collection()

    # Upsert in batches (ChromaDB has limits)
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
        )

    print(f"Indexed {len(chunks)} chunks to ChromaDB")


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
