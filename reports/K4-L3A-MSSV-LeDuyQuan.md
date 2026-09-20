# Individual contribution report

## Thông tin

- Họ và tên: Lê Duy Quân
- Mã học viên: Chưa cung cấp
- Nhóm: K4-L3A
- Repository/branch: `duyquan/task1_2_3`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 - Legal docs | Thu thập 6 tài liệu PDF về tuyển sinh đại học | `src/task1_collect_legal_docs.py`, `data/landing/legal/` | Done |
| Task 2 - News crawl | Crawl 8 bài viết tin tức về tuyển sinh | `src/task2_crawl_news.py`, `data/landing/news/` | Done |
| Task 3 - Markdown convert | Chuẩn hóa PDF/JSON sang Markdown | `src/task3_convert_markdown.py`, `data/standardized/` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng requests + BeautifulSoup thay vì Crawl4AI  
   **Lý do/evidence:** Các trang VnExpress, Tuổi Trẻ, Thanh Niên render HTML server-side, không cần JavaScript  
   **Trade-off:** Đơn giản hơn, nhanh hơn, nhưng không hỗ trợ SPA

2. **Quyết định:** Dùng MarkItDown cho PDF conversion  
   **Lý do/evidence:** Đã có trong pyproject.toml dependencies, hỗ trợ tốt tiếng Việt  
   **Trade-off:** Chất lượng conversion phụ thuộc vào cấu trúc PDF gốc

## Kiểm thử và kết quả

- Test: `pytest tests/test_acceptance.py::test_corpus_has_required_legal_documents -q`
- Test: `pytest tests/test_acceptance.py::test_corpus_has_required_news_with_metadata -q`
- Kết quả: Pass - 6 legal docs ≥ 1KB, 8 news JSON đủ metadata, 14 standardized markdown files

## Điều còn hạn chế

- Một số trang chặn crawler nên phải chọn nguồn thay thế
- Nếu có thêm thời gian, sẽ thêm nhiều nguồn hơn để tăng chất lượng corpus

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Lê Duy Quân
