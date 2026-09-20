# RAG evaluation results

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-20T10:28:36Z |
| Framework and version | Fixed-prompt LLM-as-judge runner; DeepSeek `deepseek-chat`; per-case artifact `ab_results.json` |
| Evaluator model | DeepSeek `deepseek-chat` |
| Generator model | DeepSeek `deepseek-chat` |
| Embedding model | `BAAI/bge-m3` |
| Corpus version/commit | UEH policy corpus, commit `5bb72be` |
| Golden dataset size | 15 grounded cases in `golden_dataset.json` |
| `top_k` | 5 |
| Fallback threshold and calibration | 0.30; PageIndex fallback excluded because it was not configured for either A/B arm |

## Configurations

- **Config A — dense-only:** dense retrieval with the shared BGE-M3 embedding, `top_k=5`.
- **Config B — hybrid + RRF:** dense retrieval plus BM25, fused once with RRF (`k=60`), `top_k=5`.

Both configurations are specified to use the same golden dataset, prompt, generator and evaluator. PageIndex fallback is excluded from the comparison because it is an optional provider-dependent path.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.9667 | 0.9667 | 0.0000 |
| Answer relevance | 0.8333 | 0.8333 | 0.0000 |
| Context recall | 0.8333 | 0.8200 | -0.0133 |
| Context precision | 0.6200 | 0.6133 | -0.0067 |
| **Average** | **0.8133** | **0.8083** | **-0.0050** |

The runner executed all 30 combinations (15 cases × 2 configurations) after
building a 475-chunk BGE-M3/Chroma collection. The stored per-case answer,
metric values, rationale, source IDs and retrieval time are in
`group_project/evaluation/ab_results.json`. Scores are model-judge signals,
not an independent human verdict: the same fixed DeepSeek model generated and
scored both configurations, so they are appropriate for the controlled delta
but should be reviewed alongside the saved answers.

## A/B comparison

- Cấu hình tốt hơn: **Config A (dense-only)**, nhưng chỉ hơn rất nhẹ trên recall, precision và average; faithfulness và relevance hòa nhau.
- Evidence: Dense-only đạt average `0.8133` so với `0.8083` của hybrid-RRF. Cả hai cùng bỏ lỡ chunk chứa thời hạn và địa điểm nộp hồ sơ, nên RRF hiện không cải thiện các case quan trọng này.
- Trade-off về latency/cost: Mean retrieval wall-time ghi nhận A `0.6145s`, B `0.0444s`. A chạy trước nên chịu model warm-up; không dùng chênh lệch này làm kết luận production. B vẫn thêm BM25/RRF nhưng không thêm lời gọi LLM; cần benchmark interleaved để kết luận latency.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Thời hạn nộp hồ sơ miễn giảm học phí đợt 1 năm 2026 | A & B | 1.00 | 0.00 | 0.00 | 0.00 | retrieval | Chunk `news/article_01.md::chunk-9` chứa mốc 03–05/3/2026 nhưng không vào top-5. |
| 2 | Nộp hồ sơ miễn giảm học phí ở đâu? | A & B | 1.00 | 0.00 | 0.00 | 0.00 | retrieval | Cùng bằng chứng ở `news/article_01.md::chunk-9` bị bỏ lỡ; model từ chối đúng theo context thiếu. |
| 3 | Hồ sơ miễn giảm học phí và hỗ trợ chi phí học tập cần những giấy tờ nào? | Hybrid-RRF | 0.50 | 0.50 | 0.30 | 0.40 | retrieval | Top-5 có phụ lục/mẫu đơn nhưng không có chunk-9 chứa cả hai yêu cầu hồ sơ. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Add heading-aware chunk boundaries or parent-context expansion for article notices. | Both worst questions miss the same chunk-9 although neighboring chunks are retrieved. | Raises recall for procedural questions without changing the LLM. | Re-index, rerun the same artifact and require chunk-9 in top-5 for cases 7 and 8. |
| 2 | Add query expansion for procedural terms such as “thời hạn”, “địa điểm”, “nộp hồ sơ”. | Dense and BM25 both ranked broad notice text above the answer-bearing chunk. | Improves recall of exact notice fields. | Compare the same 15 cases; report recall delta and top-5 source IDs. |
| 3 | Re-run A/B with configurations interleaved and an independent evaluator model. | Sequential warm-up invalidates the observed retrieval-time comparison; generator and judge currently share DeepSeek. | Produces defensible latency and evaluation estimates. | Save a second artifact with alternating A/B order and evaluator metadata. |

## Reproducible evaluation procedure

1. Cache the embedding model and run `python -m src.task4_chunking_indexing`.
2. Configure `LLM_PROVIDER=deepseek`, `DEEPSEEK_API_KEY` and optionally `DEEPSEEK_MODEL` in `.env`.
3. Run `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m group_project.evaluation.run_ab_evaluation`.
4. Inspect `ab_results.json`, then regenerate this table from its 30 records; retain the same `top_k=5`, model and prompt for both A/B arms.

## Quality gates run on this integration

- `python -m pytest tests/test_contracts.py -q`: 15 passed.
- `python -m pytest tests/test_acceptance.py -q`: corpus and golden dataset checks pass after this update.
