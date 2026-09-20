# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Lê Phúc Thắng
- Mã học viên: Chưa cung cấp
- Nhóm: K4-L3A
- Repository/branch: `feature/thang-rag-generation-ui`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 8 - PageIndex fallback | Tích hợp PageIndex vectorless search | `src/task8_pageindex_vectorless.py` | Done |
| Task 9 - Retrieval pipeline | Hợp nhất dense + BM25 + RRF + fallback | `src/task9_retrieval_pipeline.py` | Done |
| Task 10 - Generation | Sinh câu trả lời có citation, multi-provider LLM | `src/task10_generation.py` | Done |
| Streamlit UI | Giao diện chatbot với hiển thị sources và score | `app.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Implement lost-in-the-middle reordering cho context  
   **Lý do/evidence:** LLM có xu hướng chú ý đầu và cuối context hơn phần giữa  
   **Trade-off:** Thứ tự không theo score giảm dần, nhưng giúp LLM tận dụng tốt hơn

2. **Quyết định:** Hỗ trợ 3 LLM providers (OpenAI, Gemini, Anthropic)  
   **Lý do/evidence:** Linh hoạt cho nhóm chọn provider phù hợp với API key có sẵn  
   **Trade-off:** Code dispatch phức tạp hơn, nhưng chỉ cần cấu hình .env

## Kiểm thử và kết quả

- Test: `pytest tests/test_contracts.py::test_reorder_is_non_mutating_and_context_contains_source -q`
- Test: `streamlit run app.py` với query in-domain và out-of-domain
- Kết quả: Reorder không mutate input, context chứa source label, safe refusal hoạt động

## Điều còn hạn chế

- Chưa có conversation memory cho follow-up questions
- Nếu có thêm thời gian, sẽ thêm streaming response và conversation history context

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Nguyễn Lê Phúc Thắng
