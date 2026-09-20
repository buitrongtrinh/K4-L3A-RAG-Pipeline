# Individual contribution report

## Thông tin

- Họ và tên: Bùi Trọng Trịnh
- Mã học viên: 2A202602861
- Nhóm: RAG Pipeline — nhóm 4 thành viên
- Repository/branch: `name/buitrongtrinh_2A202602861`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Golden dataset | Soạn 15 câu hỏi grounded trên quy định học bổng, đào tạo và thông báo UEH; mỗi case có đáp án kỳ vọng và context nguồn cụ thể. | `group_project/evaluation/golden_dataset.json` | Done |
| QA & acceptance | Chạy acceptance và contract tests trên bản tích hợp; xác nhận corpus, golden dataset, schema và luồng retrieval/generation đạt các contract hiện có. | `tests/`, kết quả `5 passed` acceptance và `15 passed` contracts | Done |
| Evaluation handoff | Hoàn tất báo cáo cấu hình A/B, quality gates, phân tích ca khó và quy trình tái lập; không ghi số metric không có phép đo thật. | `group_project/evaluation/RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Golden dataset ưu tiên fact có thể đối chiếu trực tiếp trong corpus thay vì câu hỏi mở.
   **Lý do/evidence:** Mỗi trong 15 case gắn với một file và điều/mục nguồn, cho phép kiểm tra context recall, precision và citation mà không phải suy đoán ngoài dữ liệu.
   **Trade-off:** Dataset hiện tập trung vào chính sách sinh viên UEH, chưa đánh giá các chủ đề ngoài corpus.

2. **Quyết định:** Không điền điểm RAGAS ước lượng vào báo cáo khi dense model chưa tải được.
   **Lý do/evidence:** Host không phân giải được Hugging Face nên không thể cache `BAAI/bge-m3`, không có dense index để tạo A/B công bằng; báo cáo lưu rõ điều kiện và lệnh tái lập.
   **Trade-off:** Chưa có kết luận định lượng dense-only so với hybrid + RRF cho đến khi chạy được model và evaluator.

## Kiểm thử và kết quả

- `conda run -n lab-vin-env python -m pytest tests/test_acceptance.py -q`: `5 passed`.
- `conda run -n lab-vin-env python -m pytest tests/test_contracts.py -q`: `15 passed`.
- Đã kiểm tra 15 golden case đều có `question`, `expected_answer` và `expected_context` không rỗng.
- Lỗi đã phát hiện: golden dataset ban đầu rỗng và evaluation report còn placeholder; đã bổ sung dataset và báo cáo để acceptance suite pass.

## Điều còn hạn chế

- Chưa có điểm RAGAS thực tế vì model embedding BGE-M3 chưa có trong cache và môi trường không tải được từ Hugging Face.
- Nếu có thêm thời gian, tôi sẽ cache model, chạy cả hai cấu hình trên 15 case bằng cùng Gemini evaluator, rồi lưu artifact per-case và cập nhật bảng metrics.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Bùi Trọng Trịnh
