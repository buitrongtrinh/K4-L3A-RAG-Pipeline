# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | LangChain 0.4.1, ChromaDB 0.5.0, BM25Okapi 0.2.2, Ragas 0.4.3 |
| Evaluator model                    | Gemini 2.0 Flash / LLM-as-Judge |
| Generator model                    | gemini-2.0-flash (temperature=0.3, top_p=0.9) |
| Embedding model                    | BAAI/bge-m3 (1024 dimensions, dense vector cosine similarity) |
| Corpus version/commit              | 6 legal documents (PDF/DOCX standardized) + 8 news articles (JSON/Markdown) |
| Golden dataset size                | 17 grounded Q&A cases (15 in-domain tuyển sinh, 2 out-of-domain safe refusal) |
| `top_k`                            | 5 chunks |
| Fallback threshold and calibration | SCORE_THRESHOLD = 0.3 (calibrated: in-domain avg cosine 0.65-0.85; out-of-domain < 0.28) |

## Configurations

- **Config A — dense-only:** Semantic search thuần túy sử dụng ChromaDB với mô hình embedding BAAI/bge-m3 (1024 dims). Truy xuất top-5 chunks theo cosine similarity giảm dần, đưa qua reorder_for_llm (lost-in-the-middle mitigation) và sinh câu trả lời kèm citation [Document N].
- **Config B — hybrid + RRF:** Kết hợp dense semantic search (ChromaDB top-10) và sparse lexical keyword search (BM25Okapi top-10). Gộp thứ hạng một lần duy nhất bằng Reciprocal Rank Fusion (RRF, k=60) để chọn ra top-5 chunks tối ưu, kết hợp reordering và fallback kiểm soát theo best dense score < 0.3.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.824 |    0.941 |    +0.117 |
| Answer relevance  |    0.853 |    0.947 |    +0.094 |
| Context recall    |    0.765 |    0.912 |    +0.147 |
| Context precision |    0.782 |    0.888 |    +0.106 |
| **Average**       |    0.806 |    0.922 |    +0.116 |

## A/B comparison

- Cấu hình tốt hơn: Config B (Hybrid + RRF) vượt trội trên cả 4 chỉ số đánh giá cốt lõi.
- Evidence:
  - Context Recall tăng mạnh nhất (+0.147, từ 0.765 lên 0.912): BM25 bù đắp xuất sắc khi xử lý các truy vấn chứa mã viết tắt trường (UEH, HCMUT), số hiệu đề án, mốc năm (2024, 2025) mà dense embedding dễ bị phân tán do ngữ nghĩa trừu tượng.
  - Faithfulness tăng (+0.117, từ 0.824 lên 0.941): Khi context truy xuất đầy đủ và chính xác các quy định cụ thể, LLM bám sát các điều khoản thực tế, hầu như triệt tiêu hiện tượng bịa đặt thông tin (hallucination) và trích dẫn chuẩn xác [Document N].
  - Answer Relevance (+0.094) và Context Precision (+0.106): Việc gộp RRF với k=60 loại bỏ nhiễu hiệu quả, các chunk xuất hiện ở cả hai bảng xếp hạng được đẩy lên đầu, giúp câu trả lời đi thẳng vào trọng tâm câu hỏi.
- Trade-off về latency/cost:
  - Latency: Config A đạt trung bình ~42ms cho bước retrieval, trong khi Config B đạt ~48ms (chạy song song Dense embedding + BM25 in-memory + RRF calculation < 1ms). Mức tăng latency ~6ms là hoàn toàn không đáng kể đối với người dùng cuối.
  - Cost: BM25 được xây dựng và tính toán hoàn toàn cục bộ trên bộ nhớ RAM (zero API cost), không phát sinh thêm chi phí so với Config A.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Điểm chuẩn đại học năm 2024 như thế nào? | Config A | 0.60 | 0.70 | 0.60 | 0.65 | retrieval | Bảng điểm chuẩn 2024 nằm rải rác trong file đề án lớn (221KB). Semantic embedding chunk 500 ký tự cắt ngang bảng dữ liệu khiến thông tin bị phân mảnh, dense search không gom đủ các tổ hợp xét tuyển. |
|   2 | Có bao nhiêu thí sinh đăng ký thi tốt nghiệp THPT 2025? | Config A | 0.70 | 0.75 | 0.65 | 0.70 | data | Dữ liệu về số lượng đăng ký 2025 là số liệu thời sự cập nhật theo từng tuần, trong khi văn bản quy chế tuyển sinh chỉ ban hành khung chính sách, tài liệu news chỉ có ước tính chung. |
|   3 | UEH tuyển sinh năm 2025 theo phương thức nào? | Config A | 0.75 | 0.80 | 0.70 | 0.75 | retrieval | Truy vấn ngắn chứa tên viết tắt UEH. Dense embedding biểu diễn từ viết tắt kém nhạy hơn so với BM25 exact keyword matching, dẫn đến truy xuất tài liệu quy chế chung thay vì đề án riêng của UEH. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Chunking phân cấp theo cấu trúc Điều/Khoản & bảo toàn bảng số liệu Markdown | Trường hợp 1 (Điểm chuẩn) cho thấy chunk cố định 500 ký tự làm đứt đoạn các bảng điểm và điều khoản quy chế | Tăng Context Recall thêm ≥8% và Context Precision thêm ≥6% trên các câu hỏi tra cứu chỉ tiêu | Chạy lại evaluation suite trên 5 câu hỏi dạng bảng tra cứu điểm và ngành |
|        2 | Query Expansion / Synonym Dictionary cho các từ viết tắt chuyên ngành tuyển sinh (UEH, HCMUT, THPT, ĐGNL, HSA, V-SAT) | Trường hợp 3 cho thấy dense model gặp khó với tên viết tắt trường và kỳ thi nếu không có BM25 trợ lực | Tăng Context Precision lên >0.92, giảm phụ thuộc vào BM25 thuần túy | Benchmark Top-1 Retrieval Accuracy trước và sau khi thêm từ điển mở rộng |
|        3 | Dynamic Thresholding hiệu chỉnh theo độ dài câu hỏi và phân phối độ tin cậy | Fallback threshold cố định 0.3 có thể gây false negative với các câu hỏi ngắn dưới 5 từ | Giảm tỷ lệ từ chối nhầm (False Refusal Rate) xuống dưới 1% | Test với tập 20 câu hỏi ngắn in-domain và 20 câu hỏi out-of-domain |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Query Expansion (Synonyms & Acronyms) | Config B (0.922) | +0.031 | +45ms CPU / 0$ | Cải thiện rõ rệt khả năng tìm kiếm các trường đại học theo tên viết tắt (UEH, HUST, HCMUT, NEU). |
| Advanced Cross-Encoder Reranker | Config B (0.922) | +0.024 | +85ms CPU / 0$ | Cross-encoder lọc context chính xác hơn RRF tĩnh ở top-3, nhưng chi phí suy luận CPU tăng gấp đôi. |
| Conversation Multi-turn Memory | Config B (0.922) | +0.040 (follow-up Qs) | ~0ms / +5% token | Cho phép thí sinh hỏi tiếp các bước nộp hồ sơ hoặc hỏi chi tiết theo ngành mà không phải lặp lại ngữ cảnh. |
| Streamlit Interactive Citation UI & Highlight | Standard UI | UI Experience +100% | 0ms / 0$ | Trực quan hóa nguồn trích dẫn, cho phép xem preview chunk, score, và đối chiếu song song dense vs sparse. |
