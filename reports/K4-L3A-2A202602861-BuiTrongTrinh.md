# Individual contribution report

## Thông tin

- Họ và tên: Bùi Trọng Trịnh
- Mã học viên: 2A202602861
- Nhóm: K4-L3A
- Repository/branch: `name/buitrongtrinh_2A202602861`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Golden dataset | Tạo 17 golden Q&A cases từ corpus tuyển sinh | `group_project/evaluation/golden_dataset.json` | Done |
| Evaluation A/B | Chạy evaluation 4 metrics, so sánh dense-only vs hybrid+RRF | `src/evaluate.py`, `group_project/evaluation/RESULT.md` | Done |
| Documentation | README, TEAMMATES.md, individual reports | `README.md`, `TEAMMATES.md`, `reports/` | Done |
| Test & QA | Chạy contract tests và acceptance tests, kiểm tra pipeline | `pytest -q` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng LLM-as-judge cho 4 metrics thay vì RAGAS framework  
   **Lý do/evidence:** RAGAS 0.4.3 yêu cầu cấu hình phức tạp; LLM-as-judge cho phép đánh giá nhanh với cùng 4 metrics  
   **Trade-off:** Kết quả phụ thuộc vào model evaluator, không có ground truth standardized

2. **Quyết định:** Golden dataset bao gồm 2 out-of-domain cases  
   **Lý do/evidence:** Cần test safe refusal khi query ngoài domain tuyển sinh  
   **Trade-off:** 2/17 cases không đánh giá retrieval quality, nhưng quan trọng cho user experience

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py -q` và `pytest tests/test_acceptance.py -q`
- Kết quả: Tất cả tests passed
- Lỗi đã phát hiện và cách xử lý: Golden dataset ban đầu thiếu expected_context field → bổ sung cho tất cả cases

## Điều còn hạn chế

- Golden dataset được tạo trước khi crawl thực tế → expected_answer có thể không khớp chính xác với nội dung corpus
- Nếu có thêm thời gian, sẽ tạo golden dataset từ nội dung corpus đã standardized

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Bùi Trọng Trịnh
