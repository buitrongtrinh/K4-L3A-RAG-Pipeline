# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Lê Phúc Thắng
- Mã học viên: 2A202602638
- Nhóm: RAG Pipeline — nhóm 4 thành viên
- Repository/branch: `name/nguyenlephucthang-2A202602638`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 8 — PageIndex fallback | Tạo client theo API key, cache document ID để tránh upload lại, giới hạn file hỗ trợ và chuyển kết quả thành `SearchResult` có method `pageindex`. | `src/task8_pageindex_vectorless.py`, commit `ee2953a` | Done |
| Task 9 — Retrieval integration | Kết hợp dense và BM25 bằng RRF một lần; dùng dense score gốc cho fallback và trả hybrid khi PageIndex lỗi. | `src/task9_retrieval_pipeline.py`, commit `ee2953a` | Done |
| Task 10 — Generation & citation | Reorder context, gắn title/source vào context, gọi OpenAI/Gemini/Anthropic theo cấu hình, và trả safe refusal nếu thiếu evidence hoặc provider lỗi. | `src/task10_generation.py`, commit `ee2953a` | Done |
| Chatbot UI | Kết nối Streamlit UI với generation result và hiển thị nguồn retrieval cho người dùng. | `app.py`, commit `ee2953a` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** PageIndex là fallback tùy chọn, không được làm hỏng retrieval chính khi API key, SDK hoặc provider không sẵn sàng.
   **Lý do/evidence:** `retrieve()` bắt exception từ fallback và trả hybrid result; `pageindex_search()` trả danh sách rỗng khi chưa cấu hình dịch vụ.
   **Trade-off:** Khi fallback chưa cấu hình, câu hỏi confidence thấp chỉ có kết quả hybrid hoặc safe refusal thay vì nguồn PageIndex.

2. **Quyết định:** Quyết định fallback dựa trên dense cosine-derived score, không dựa trên RRF score.
   **Lý do/evidence:** RRF chỉ biểu diễn thứ hạng giữa dense và BM25; contract test kiểm tra chính xác điều kiện này.
   **Trade-off:** Cần giữ dense result song song với fused result cho đến khi hoàn tất quyết định fallback.

## Kiểm thử và kết quả

- `conda run -n lab-vin-env python -m pytest tests/test_contracts.py -q -k 'reorder or retrieve'`: `4 passed` cho các hành vi integration/generation của Task 9–10.
- Sau khi tích hợp tất cả module: `conda run -n lab-vin-env python -m pytest -q`: `20 passed`.
- Đã kiểm tra `python -m py_compile src/task8_pageindex_vectorless.py src/task9_retrieval_pipeline.py src/task10_generation.py app.py` thành công.
- Lỗi đã phát hiện: nhánh ban đầu chưa nhận Task 4–7; đã merge `main` vào nhánh trước khi chạy full contract suite, sau đó toàn bộ `15` contract tests pass.

## Điều còn hạn chế

- PageIndex chỉ chạy khi có API key và SDK/provider tương thích; integration test dùng mock để không gọi dịch vụ ngoài.
- Nếu có thêm thời gian, tôi sẽ chạy demo end-to-end có key provider, lưu latency và kiểm tra citation trên các golden cases có dense score thấp.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Nguyễn Lê Phúc Thắng
