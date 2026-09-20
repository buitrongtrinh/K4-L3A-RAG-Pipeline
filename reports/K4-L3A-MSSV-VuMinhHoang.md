# Individual contribution report

## Thông tin

- Họ và tên: Vũ Minh Hoàng
- Mã học viên: Chưa cung cấp
- Nhóm: K4-L3A
- Repository/branch: `feature/hoang-hybrid-retrieval`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 - Chunking & Indexing | Chunking recursive, BGE-M3 embedding, ChromaDB upsert | `src/task4_chunking_indexing.py` | Done |
| Task 5 - Semantic search | Dense search với cosine similarity | `src/task5_semantic_search.py` | Done |
| Task 6 - Lexical search | BM25 search trên corpus chunks | `src/task6_lexical_search.py` | Done |
| Task 7 - RRF Reranking | Reciprocal Rank Fusion gộp dense + BM25 | `src/task7_reranking.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Giữ CHUNK_SIZE=500, CHUNK_OVERLAP=50 với recursive splitting  
   **Lý do/evidence:** Corpus tuyển sinh có nhiều đoạn ngắn, 500 tokens đủ giữ ngữ cảnh  
   **Trade-off:** Chunk nhỏ hơn có thể chính xác hơn nhưng mất context

2. **Quyết định:** Sử dụng BAAI/bge-m3 cho embedding  
   **Lý do/evidence:** BGE-M3 hỗ trợ đa ngôn ngữ tốt, bao gồm tiếng Việt; dimension 1024  
   **Trade-off:** Model lớn hơn các model embedding nhẹ, nhưng chất lượng tốt hơn

## Kiểm thử và kết quả

- Test: `pytest tests/test_contracts.py -q`
- Kết quả: Tất cả contract tests passed
- Đã kiểm tra: RRF score đúng công thức, dense/BM25 sort giảm dần, unique IDs

## Điều còn hạn chế

- BM25 tokenization dùng simple split, chưa có tiền xử lý tiếng Việt
- Nếu có thêm thời gian, sẽ thử VnCoreNLP tokenizer cho BM25

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Vũ Minh Hoàng
