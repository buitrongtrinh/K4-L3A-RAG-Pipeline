"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://dantri.com.vn/giao-duc/bo-gddt-thay-doi-ke-hoach-siet-phuong-thuc-xet-tuyen-dai-hoc-20260917222502528.htm",
    "https://dantri.com.vn/giao-duc/bo-gddt-tinh-bo-diem-cong-ielts-giai-hoc-sinh-gioi-khi-tuyen-sinh-dai-hoc-20260918075956503.htm",
    "https://dantri.com.vn/giao-duc/bo-cong-diem-ielts-siet-phuong-thuc-tuyen-sinh-can-nhung-dung-de-soc-20260918140159505.htm",
    "https://dantri.com.vn/giao-duc/bo-gddt-yeu-cau-cham-dut-tinh-trang-nang-diem-lam-dep-hoc-ba-20260920092759061.htm",
    "https://vnexpress.net/phu-huynh-thi-sinh-choi-voi-vi-du-kien-siet-phuong-thuc-tuyen-sinh-dai-hoc-5121727.html",
    "https://vnexpress.net/giu-ky-thi-tot-nghiep-thpt-voi-da-muc-tieu-5122460.html",
    "https://vnexpress.net/sap-xep-doi-ten-hang-loat-nganh-o-dai-hoc-5121259.html",
    "https://vnexpress.net/nhieu-hoc-sinh-lo-mat-loi-the-neu-bo-cong-diem-ielts-5122195.html",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}


def clean_text(text: str) -> str:
    """Remove excessive whitespace and clean up text."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def extract_article_content(html: str, url: str) -> dict:
    """Extract article title and content from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, styles, nav, footer
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Extract title
    title = ""
    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text(strip=True)
    elif soup.find("title"):
        title = soup.find("title").get_text(strip=True)

    # Extract main content - try common article selectors
    content = ""
    article_selectors = [
        {"class_": "fck_detail"},           # VnExpress
        {"class_": "detail-content"},       # Tuoi Tre
        {"class_": "detail__content"},      # Thanh Nien
        {"class_": "singular-content"},     # Dan Tri
        {"class_": "article-content"},      # Generic
        {"class_": "entry-content"},        # Generic
    ]

    article_body = None
    for selector in article_selectors:
        article_body = soup.find("div", **selector)
        if article_body:
            break

    if not article_body:
        article_body = soup.find("article")

    if article_body:
        # Convert to markdown-like text
        paragraphs = []
        for element in article_body.find_all(["p", "h2", "h3", "h4", "li", "blockquote"]):
            text = element.get_text(strip=True)
            if text:
                if element.name in ("h2", "h3", "h4"):
                    level = int(element.name[1])
                    paragraphs.append(f"\n{'#' * level} {text}\n")
                elif element.name == "li":
                    paragraphs.append(f"- {text}")
                elif element.name == "blockquote":
                    paragraphs.append(f"> {text}")
                else:
                    paragraphs.append(text)
        content = "\n\n".join(paragraphs)
    else:
        # Fallback: get all text from body
        body = soup.find("body")
        if body:
            content = body.get_text(separator="\n\n", strip=True)

    content = clean_text(content)

    return {
        "url": url,
        "title": title or "Unknown",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content,
    }


async def crawl_article(url: str) -> dict:
    """Crawl a single article using requests + BeautifulSoup."""
    response = requests.get(url, timeout=30, headers=HEADERS)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    return extract_article_content(response.text, url)


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            if len(article["content_markdown"]) < 100:
                print(f"Warning: Short content for {url} ({len(article['content_markdown'])} chars)")
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output} — {article['title'][:60]}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
