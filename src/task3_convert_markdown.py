"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

import json
from pathlib import Path

from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF/DOCX vào standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not legal_dir.exists():
        print(f"Warning: {legal_dir} does not exist")
        return

    converter = MarkItDown()

    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            output_path = output_dir / f"{path.stem}.md"
            try:
                result = converter.convert(str(path))
                content = result.text_content

                # Add metadata header
                header = (
                    f"# {path.stem}\n\n"
                    f"**Source:** {path.name}\n\n"
                    f"**Type:** legal\n\n---\n\n"
                )

                full_content = header + content

                if len(full_content.strip()) < 200:
                    print(f"Warning: Very short content from {path.name} ({len(full_content)} chars)")

                output_path.write_text(full_content, encoding="utf-8")
                print(f"Converted: {path.name} -> {output_path.name} ({len(full_content)} chars)")
            except Exception as e:
                print(f"Failed to convert {path.name}: {e}")


def convert_news_articles() -> None:
    """Convert JSON vào standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not news_dir.exists():
        print(f"Warning: {news_dir} does not exist")
        return

    for path in sorted(news_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            header = (
                f"# {data['title']}\n\n"
                f"**Source:** {data['url']}\n\n"
                f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
            )
            content = header + data["content_markdown"]

            if len(content.strip()) < 200:
                print(f"Warning: Very short content from {path.name} ({len(content)} chars)")

            output_path = output_dir / f"{path.stem}.md"
            output_path.write_text(content, encoding="utf-8")
            print(f"Converted: {path.name} -> {output_path.name} ({len(content)} chars)")
        except Exception as e:
            print(f"Failed to convert {path.name}: {e}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
