# GSEB Chunk Quality & Lexical Retrieval Audit Report

- **Quality Gate Verdict**: **`PASS`**
- **Total Chunks Evaluated**: 563
- **Average Chunk Size**: 451.1 tokens (Median: 510.0)
- **Token Distribution**: Min: 14, P25: 83.0, P75: 657.0, P95: 790.0, Max: 1580
- **Detected Anomalies**: 17 (3.02%)

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
| `chk_7ba6bdee7618c98d` | `TOO_LONG` | 1580 | Chunk is excessively long (1580 tokens) | `STD-10th/Std-10_Science_English Medium.pdf` p.193 |
| `chk_5d15faf7ea42af7b` | `BROKEN_UNICODE` | 552 | Contains unresolved raw font glyph markers (/G<n>) | `STD-10th/Std-10_Maths_EnglishMedium.pdf` p.194 |
| `chk_1e2bf818a4e89f9c` | `BROKEN_UNICODE` | 470 | Contains unresolved raw font glyph markers (/G<n>) | `STD-10th/Std-10_Maths_EnglishMedium.pdf` p.237 |
| `659c2847-5c1f-4b48-96b0-cfc8f1298c5c` | `TOO_SHORT` | 29 | Chunk has only 29 tokens | `STD-10/Std-10_Science_English Medium.pdf` p.16 |
| `chunk_d8e3396b` | `TOO_SHORT` | 14 | Chunk has only 14 tokens | `STD-10/Std-10_Science_English Medium.pdf` p.148 |
| `chunk_0a40d615` | `TOO_SHORT` | 14 | Chunk has only 14 tokens | `STD-10/Std-10_Science_English Medium.pdf` p.40 |
| `chunk_f935fc42` | `TOO_SHORT` | 28 | Chunk has only 28 tokens | `STD-10/Std-10_Social_Science_EnglishMedium.pdf` p.1 |
| `chunk_ab35056f` | `TOO_SHORT` | 27 | Chunk has only 27 tokens | `STD-10/Std-10_ComputerStudies_EnglishMedium.pdf` p.1 |
| `chunk_bc163adf` | `TOO_SHORT` | 27 | Chunk has only 27 tokens | `STD-10/Std-10_ComputerStudies_EnglishMedium.pdf` p.90 |
| `chunk_ae6422a8` | `TOO_SHORT` | 27 | Chunk has only 27 tokens | `STD-10/Std-10_Black-Buck_Supplementry_Reader.pdf` p.1 |
| `chunk_767367f7` | `TOO_SHORT` | 21 | Chunk has only 21 tokens | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.68 |
| `chunk_4878bb68` | `TOO_SHORT` | 25 | Chunk has only 25 tokens | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.77 |
| `chunk_d2c8ff78` | `TOO_SHORT` | 29 | Chunk has only 29 tokens | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.129 |
| `chunk_78536fe8` | `TOO_SHORT` | 22 | Chunk has only 22 tokens | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.188 |
| `chunk_9969c79a` | `TOO_SHORT` | 17 | Chunk has only 17 tokens | `STD-10/Std-10_Maths_EnglishMedium.pdf` p.189 |
