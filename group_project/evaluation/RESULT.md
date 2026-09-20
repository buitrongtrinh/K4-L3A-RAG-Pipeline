# RAG evaluation results

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-20 |
| Framework and version | RAGAS 0.4.3 (declared dependency); offline contract and acceptance checks run with pytest 9.1.1 |
| Evaluator model | Gemini evaluator is configured, but no metric run was completed in this environment |
| Generator model | Gemini provider is configured; no generation run is recorded here |
| Embedding model | `BAAI/bge-m3` |
| Corpus version/commit | UEH policy corpus, integration commit `514cf94` |
| Golden dataset size | 15 grounded cases in `golden_dataset.json` |
| `top_k` | 5 |
| Fallback threshold and calibration | 0.30; must be calibrated on the golden set once the embedding model is available locally |

## Configurations

- **Config A — dense-only:** dense retrieval with the shared BGE-M3 embedding, `top_k=5`.
- **Config B — hybrid + RRF:** dense retrieval plus BM25, fused once with RRF (`k=60`), `top_k=5`.

Both configurations are specified to use the same golden dataset, prompt, generator and evaluator. PageIndex fallback is excluded from the comparison because it is an optional provider-dependent path.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
| --- | ---: | ---: | ---: |
| Faithfulness | Not measured | Not measured | Not measured |
| Answer relevance | Not measured | Not measured | Not measured |
| Context recall | Not measured | Not measured | Not measured |
| Context precision | Not measured | Not measured | Not measured |
| **Average** | **Not measured** | **Not measured** | **Not measured** |

Numerical RAGAS scores are intentionally not fabricated. The BGE-M3 model was not cached, and this environment could not resolve Hugging Face to download the missing model files. Consequently, a dense index and a like-for-like A/B generation run could not be completed. The Gemini credential alone does not resolve that dependency.

## A/B comparison

- Cấu hình tốt hơn: Chưa kết luận khi chưa có phép đo cùng điều kiện.
- Evidence: Contract test confirms the comparison path is structurally valid: dense and BM25 return the common schema, RRF is applied once, and fallback uses the original dense score.
- Trade-off về latency/cost: Config B adds BM25 scoring and RRF but should not add a second embedding call; the actual latency and token cost must be captured during the reproducible run.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Multi-condition scholarship eligibility | Pending run | Not measured | Not measured | Not measured | Not measured | retrieval | Multiple conditions can be split across chunks. |
| 2 | Tuition-support eligibility and documents | Pending run | Not measured | Not measured | Not measured | Not measured | retrieval/generation | Notice includes annex references and several beneficiary groups. |
| 3 | Insurance onboarding for new students | Pending run | Not measured | Not measured | Not measured | Not measured | data | Long notice contains repeated navigation content near the answer. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Cache or pre-download `BAAI/bge-m3`, then rebuild ChromaDB. | The current host cannot download the model, blocking dense evaluation. | Enables the actual A/B run. | `python -m src.task4_chunking_indexing` completes and persists the collection. |
| 2 | Run both configurations over all 15 golden cases and save per-case outputs. | No numerical metric result is currently claimed. | Produces reproducible faithfulness, relevance, recall and precision scores. | Execute the RAGAS runner with the same model, prompt and `top_k`. |
| 3 | Review chunks around multi-condition policies and navigation-heavy notices. | The identified hard cases need precise supporting context. | Improves context precision and grounded citations. | Compare per-case context precision before and after chunking changes. |

## Reproducible evaluation procedure

1. Cache the embedding model and run `python -m src.task4_chunking_indexing`.
2. Run Config A and Config B for every item in `golden_dataset.json`, saving answer and retrieved contexts.
3. Use the same Gemini evaluator, generator, prompt and `top_k=5` for both configurations.
4. Compute RAGAS faithfulness, answer relevance, context recall and context precision, then replace the `Not measured` cells with the exported values and link the per-case artifact.

## Quality gates run on this integration

- `python -m pytest tests/test_contracts.py -q`: 15 passed.
- `python -m pytest tests/test_acceptance.py -q`: corpus and golden dataset checks pass after this update.
