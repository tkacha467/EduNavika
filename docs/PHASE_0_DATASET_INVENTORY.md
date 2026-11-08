# Phase 0 Dataset Inventory

## Observed file inventory

| Scope | Count / state |
|---|---|
| Files under `GSEB-Dataset` | 165 |
| PDFs under `GSEB-Dataset` | 159 |
| Textbook manifest PDF count | 86 |
| Textbook manifest pages | 14,252 |
| Textbook source coverage | Std 9-12 GSEB English-medium, including Science, Mathematics, Biology, Chemistry, Physics and non-target subjects |
| Separate competitive-paper directories | `GSEB-Dataset/Dataset/Dataset/jee` and `.../Neet` |
| NEET 2021 diagram assets | 41 PNGs under `backend/static/assets/diagrams/neet_2021` |

The manifest is detailed for the textbook corpus but does not constitute a complete competitive-paper metadata register. A reproducible per-paper inventory must still record examination, year, session, booklet, source checksum, answer-key source, rights state, parse result, diagram state, topic mapping, and serving eligibility.

## Verified competitive artifact

`data/processed/neet_2021_answer_key_reconciliation_report.json` identifies NEET UG 2021 booklet M4, cites an NTA final-key document, declares 200 questions, and records 187 text questions plus 13 diagram-dependent questions. It records `rights_status: PENDING_LEGAL_REVIEW` and `publish_permission: FORBIDDEN` for diagram items. This is evidence of a specific audit artifact, not release permission for the corpus.

## Data readiness classification

- Textbooks: **partially catalogued**, extraction quality varies and many PDFs require OCR/hybrid handling.
- JEE/NEET PDFs: **present but not release-inventoried**; coverage, metadata and rights remain incomplete.
- Answer keys: **verified for the named NEET 2021 M4 artifact only**; do not generalize to every paper.
- Diagrams: **partially extracted**; visual review and publication clearance remain required.
- Student longitudinal data: **not demonstrated as sufficient** for model training or prediction claims.
