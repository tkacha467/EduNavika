# GSEB Chunk Quality & Lexical Retrieval Audit Report

- **Quality Gate Verdict**: **`PASS`**
- **Total Chunks Evaluated**: 545
- **Average Chunk Size**: 566.9 tokens (Median: 557.0)
- **Token Distribution**: Min: 8, P25: 468.0, P75: 684.0, P95: 801.0, Max: 1580
- **Detected Anomalies**: 7 (1.28%)

---

## Deterministic Lexical Retrieval Benchmark (BM25)

- **Recall@1**: 100.0%
- **Recall@5**: 100.0%
- **Recall@10**: 100.0%
- **Mean Reciprocal Rank (MRR)**: 1.000

| Query ID | Subject | First Relevant Rank | R@1 | R@5 | R@10 | Reciprocal Rank | Top Preview |
|----------|---------|---------------------|-----|-----|------|-----------------|-------------|
| Q1 | Mathematics | 1 | ✅ | ✅ | ✅ | 1.000 | PROOFS IN MA THEMA TICS 235 lSo, we begin by assuming that t... |
| Q2 | Mathematics | 1 | ✅ | ✅ | ✅ | 1.000 | REAL NUMBERS 3 An equivalent version of Theorem 1.1 was prob... |
| Q3 | Science | 1 | ✅ | ✅ | ✅ | 1.000 | Science2 Activity 1.2Activity 1.2Activity 1.2Activity 1.2Act... |
| Q4 | Science | 1 | ✅ | ✅ | ✅ | 1.000 | Science34 /square6The strength of an acid or an alkali can b... |
| Q5 | First Flight | 1 | ✅ | ✅ | ✅ | 1.000 |   T HE house — the only one in the entire va... |
| Q6 | First Flight | 1 | ✅ | ✅ | ✅ | 1.000 |    • ”Apartheid’ is a political system that s... |

---

## Sample Anomalies Sampled

| Chunk ID | Issue Type | Tokens | Details | Source |
|----------|------------|--------|---------|--------|
| `chk_cb5ba5feed912b30` | `TOO_SHORT` | 11 | Chunk has only 11 tokens | `STD-10/Std-10_Black-Buck_Supplementry_Reader.pdf` p.2 |
| `chk_2086f1b64d7dd501` | `TOO_SHORT` | 20 | Chunk has only 20 tokens | `STD-10/Std-10_English Second Language.pdf` p.3 |
| `chk_08df27906aaf7de7` | `BROKEN_UNICODE` | 552 | Contains unresolved raw font glyph markers (/G<n>) | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.194 |
| `chk_7e962356ac57d3fd` | `BROKEN_UNICODE` | 470 | Contains unresolved raw font glyph markers (/G<n>) | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.237 |
| `chk_7ba6bdee7618c98d` | `TOO_LONG` | 1580 | Chunk is excessively long (1580 tokens) | `STD-10/Std-10_Science_English Medium.pdf` p.193 |
| `chk_585ed616fd95f394` | `TOO_SHORT` | 12 | Chunk has only 12 tokens | `STD-10/Std-10_Social_Science_EnglishMedium.pdf` p.3 |
| `chk_cc5d72e1988183c5` | `TOO_SHORT` | 8 | Chunk has only 8 tokens | `STD-10/Std_10_Yoga, Health and Physical Education_Eng_M.pdf` p.3 |
