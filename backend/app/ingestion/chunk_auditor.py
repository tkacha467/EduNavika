import re
import math
import json
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from backend.app.core.database import SessionLocal
from backend.app.models.content import LearningContent
from backend.app.models.curriculum import Topic, Chapter, Subject, Standard


class ChunkAnomaly(BaseModel):
    chunk_id: str
    issue_type: str  # TOO_SHORT, TOO_LONG, HEADER_CONTAMINATION, BROKEN_UNICODE, MID_SENTENCE_CUT
    details: str
    token_count: int
    source_document: Optional[str]
    source_page: Optional[int]


class RetrievalQuery(BaseModel):
    query_id: str
    query_text: str
    target_subject: str
    expected_keywords: List[str]
    target_chapter_hint: Optional[str] = None


class RetrievalResult(BaseModel):
    query_id: str
    query_text: str
    target_subject: str
    top_chunk_id: Optional[str]
    top_score: float
    top_preview: str
    rank_of_first_relevant: Optional[int]  # 1-indexed, None if not in top 10
    is_recall_at_1: bool
    is_recall_at_5: bool
    is_recall_at_10: bool
    reciprocal_rank: float


class ChunkAuditReport(BaseModel):
    total_chunks_evaluated: int
    min_tokens: int
    max_tokens: int
    avg_tokens: float
    median_tokens: float
    p25_tokens: float
    p75_tokens: float
    p95_tokens: float
    anomalies_count: int
    anomalies: List[ChunkAnomaly]
    retrieval_queries_tested: int
    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    mrr: float
    quality_gate_status: str  # PASS, CONDITIONAL_PASS, FAIL
    retrieval_results: List[RetrievalResult]


class BM25Index:
    """Deterministic Okapi BM25 implementation for zero-dependency retrieval benchmarking."""

    def __init__(self, corpus: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_len = []
        self.doc_freqs: Dict[str, int] = Counter()
        self.docs_tokens: List[List[str]] = []
        self.avg_doc_len = 0.0

        total_len = 0
        for doc in corpus:
            tokens = self._tokenize(doc["text"])
            self.docs_tokens.append(tokens)
            length = len(tokens)
            self.doc_len.append(length)
            total_len += length

            seen = set(tokens)
            for t in seen:
                self.doc_freqs[t] += 1

        self.N = len(corpus)
        self.avg_doc_len = (total_len / self.N) if self.N > 0 else 0.0

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\b[a-z0-9]+\b", text.lower())

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        query_tokens = self._tokenize(query)
        scores = [0.0] * self.N

        for token in query_tokens:
            if token not in self.doc_freqs:
                continue
            df = self.doc_freqs[token]
            # Standard Lucene/BM25 IDF
            idf = math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))

            for idx, doc_toks in enumerate(self.docs_tokens):
                tf = doc_toks.count(token)
                if tf == 0:
                    continue
                d_len = self.doc_len[idx]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (d_len / self.avg_doc_len))
                scores[idx] += idf * (numerator / denominator)

        # Rank documents
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


class ChunkAuditor:
    """
    Phase 4: Chunk Quality & Lexical Retrieval Auditor.
    Validates chunk boundary hygiene, token distribution, lack of noise/artifacts,
    and conducts deterministic BM25 retrieval benchmarking.
    """

    CURATED_QUERIES: List[RetrievalQuery] = [
        RetrievalQuery(
            query_id="Q1",
            query_text="Euclid's division lemma states that for given positive integers a and b there exist unique integers q and r",
            target_subject="Mathematics",
            expected_keywords=["euclid", "division", "lemma", "integers", "remainder"],
            target_chapter_hint="Real Numbers"
        ),
        RetrievalQuery(
            query_id="Q2",
            query_text="Fundamental theorem of arithmetic every composite number can be expressed as a product of primes",
            target_subject="Mathematics",
            expected_keywords=["fundamental", "theorem", "arithmetic", "composite", "prime"],
            target_chapter_hint="Real Numbers"
        ),
        RetrievalQuery(
            query_id="Q3",
            query_text="Chemical reactions and equations magnesium ribbon burns with a dazzling white flame",
            target_subject="Science",
            expected_keywords=["magnesium", "ribbon", "flame", "chemical", "oxide"],
            target_chapter_hint="Chemical Reactions"
        ),
        RetrievalQuery(
            query_id="Q4",
            query_text="Acids bases and salts litmus paper turns red or blue phenolphthalein indicator",
            target_subject="Science",
            expected_keywords=["acid", "base", "litmus", "indicator", "salt"],
            target_chapter_hint="Acids"
        ),
        RetrievalQuery(
            query_id="Q5",
            query_text="Lencho was a dedicated farmer who prayed for rain to nourish his field of ripe corn",
            target_subject="First Flight",
            expected_keywords=["lencho", "farmer", "corn", "rain", "hailstones"],
            target_chapter_hint="Letter to God"
        ),
        RetrievalQuery(
            query_id="Q6",
            query_text="Nelson Mandela inauguration as first black President of South Africa at the Union Buildings amphitheatre",
            target_subject="First Flight",
            expected_keywords=["mandela", "inauguration", "president", "africa", "amphitheatre"],
            target_chapter_hint="Nelson Mandela"
        ),
    ]

    def __init__(self, output_dir: Path = Path("data/processed/reports")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_audit(self) -> ChunkAuditReport:
        db = SessionLocal()
        try:
            db_chunks = (
                db.query(LearningContent)
                .join(Topic, LearningContent.topic_id == Topic.id)
                .join(Chapter, Topic.chapter_id == Chapter.id)
                .join(Subject, Chapter.subject_id == Subject.id)
                .all()
            )

            corpus: List[Dict[str, Any]] = []
            token_counts: List[int] = []
            anomalies: List[ChunkAnomaly] = []

            for c in db_chunks:
                text = c.content_text or ""
                # Approx tokens: word count + rough char ratio
                approx_tokens = max(1, int(len(text) / 4.2))
                token_counts.append(approx_tokens)

                corpus.append({
                    "id": c.chunk_identifier or str(c.id),
                    "text": text,
                    "title": c.title,
                    "document": c.source_document,
                    "page": c.source_page,
                    "subject": c.topic.chapter.subject.name if c.topic and c.topic.chapter and c.topic.chapter.subject else "",
                    "chapter": c.topic.chapter.title if c.topic and c.topic.chapter else "",
                })

                # Check for anomalies
                if approx_tokens < 30:
                    anomalies.append(ChunkAnomaly(
                        chunk_id=c.chunk_identifier or str(c.id),
                        issue_type="TOO_SHORT",
                        details=f"Chunk has only {approx_tokens} tokens",
                        token_count=approx_tokens,
                        source_document=c.source_document,
                        source_page=c.source_page,
                    ))
                elif approx_tokens > 1000:
                    anomalies.append(ChunkAnomaly(
                        chunk_id=c.chunk_identifier or str(c.id),
                        issue_type="TOO_LONG",
                        details=f"Chunk is excessively long ({approx_tokens} tokens)",
                        token_count=approx_tokens,
                        source_document=c.source_document,
                        source_page=c.source_page,
                    ))

                # Contamination checks
                if "/g" in text.lower() and re.search(r"/G\d+", text):
                    anomalies.append(ChunkAnomaly(
                        chunk_id=c.chunk_identifier or str(c.id),
                        issue_type="BROKEN_UNICODE",
                        details="Contains unresolved raw font glyph markers (/G<n>)",
                        token_count=approx_tokens,
                        source_document=c.source_document,
                        source_page=c.source_page,
                    ))

                if re.search(r"STD-\d+.*Chapter\s+\d+", text[:80], re.IGNORECASE):
                    anomalies.append(ChunkAnomaly(
                        chunk_id=c.chunk_identifier or str(c.id),
                        issue_type="HEADER_CONTAMINATION",
                        details="Top of chunk contains unstripped running header",
                        token_count=approx_tokens,
                        source_document=c.source_document,
                        source_page=c.source_page,
                    ))

            token_counts.sort()
            total_chunks = len(token_counts)
            if total_chunks == 0:
                raise ValueError("No chunks found in database to audit!")

            min_tok = token_counts[0]
            max_tok = token_counts[-1]
            avg_tok = sum(token_counts) / total_chunks
            med_tok = token_counts[total_chunks // 2]
            p25 = token_counts[int(total_chunks * 0.25)]
            p75 = token_counts[int(total_chunks * 0.75)]
            p95 = token_counts[int(total_chunks * 0.95)]

            # Build BM25 index & run retrieval benchmark
            bm25 = BM25Index(corpus)
            retrieval_results: List[RetrievalResult] = []

            recall_1_count = 0
            recall_5_count = 0
            recall_10_count = 0
            rr_sum = 0.0

            for q in self.CURATED_QUERIES:
                ranked = bm25.search(q.query_text, top_k=10)
                first_relevant_rank = None

                top_chunk_id = None
                top_score = 0.0
                top_preview = ""

                if ranked:
                    top_idx, top_score = ranked[0]
                    top_doc = corpus[top_idx]
                    top_chunk_id = top_doc["id"]
                    top_preview = top_doc["text"][:150].replace("\n", " ")

                # Find first relevant item in top 10
                for rank_idx, (doc_idx, score) in enumerate(ranked):
                    doc = corpus[doc_idx]
                    text_lower = doc["text"].lower()
                    # Check if matching key criteria
                    matches = sum(1 for kw in q.expected_keywords if kw.lower() in text_lower)
                    is_match = (matches >= 2) or (
                        q.target_chapter_hint and q.target_chapter_hint.lower() in doc["chapter"].lower()
                    )
                    if is_match and first_relevant_rank is None:
                        first_relevant_rank = rank_idx + 1
                        break

                r1 = (first_relevant_rank == 1)
                r5 = (first_relevant_rank is not None and first_relevant_rank <= 5)
                r10 = (first_relevant_rank is not None and first_relevant_rank <= 10)
                rr = (1.0 / first_relevant_rank) if first_relevant_rank else 0.0

                if r1:
                    recall_1_count += 1
                if r5:
                    recall_5_count += 1
                if r10:
                    recall_10_count += 1
                rr_sum += rr

                retrieval_results.append(RetrievalResult(
                    query_id=q.query_id,
                    query_text=q.query_text,
                    target_subject=q.target_subject,
                    top_chunk_id=top_chunk_id,
                    top_score=round(top_score, 3),
                    top_preview=top_preview,
                    rank_of_first_relevant=first_relevant_rank,
                    is_recall_at_1=r1,
                    is_recall_at_5=r5,
                    is_recall_at_10=r10,
                    reciprocal_rank=round(rr, 3),
                ))

            q_total = len(self.CURATED_QUERIES)
            rec_1 = recall_1_count / q_total if q_total > 0 else 0.0
            rec_5 = recall_5_count / q_total if q_total > 0 else 0.0
            rec_10 = recall_10_count / q_total if q_total > 0 else 0.0
            mrr = rr_sum / q_total if q_total > 0 else 0.0

            # Quality gate
            # PASS: Recall@5 >= 80%, MRR >= 0.60, anomalies <= 5% of total chunks
            anomaly_ratio = len(anomalies) / total_chunks
            if rec_5 >= 0.80 and mrr >= 0.60 and anomaly_ratio <= 0.05:
                status = "PASS"
            elif rec_5 >= 0.60 and mrr >= 0.40:
                status = "CONDITIONAL_PASS"
            else:
                status = "FAIL"

            report = ChunkAuditReport(
                total_chunks_evaluated=total_chunks,
                min_tokens=min_tok,
                max_tokens=max_tok,
                avg_tokens=round(avg_tok, 1),
                median_tokens=med_tok,
                p25_tokens=p25,
                p75_tokens=p75,
                p95_tokens=p95,
                anomalies_count=len(anomalies),
                anomalies=anomalies[:50],  # cap list to 50 for reporting
                retrieval_queries_tested=q_total,
                recall_at_1=round(rec_1, 3),
                recall_at_5=round(rec_5, 3),
                recall_at_10=round(rec_10, 3),
                mrr=round(mrr, 3),
                quality_gate_status=status,
                retrieval_results=retrieval_results,
            )

            self._export_reports(report)
            return report
        finally:
            db.close()

    def _export_reports(self, report: ChunkAuditReport):
        json_path = self.output_dir / "chunk_quality_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)

        md_path = self.output_dir / "chunk_quality_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# GSEB Chunk Quality & Lexical Retrieval Audit Report\n\n")
            f.write(f"- **Quality Gate Verdict**: **`{report.quality_gate_status}`**\n")
            f.write(f"- **Total Chunks Evaluated**: {report.total_chunks_evaluated}\n")
            f.write(f"- **Average Chunk Size**: {report.avg_tokens} tokens (Median: {report.median_tokens})\n")
            f.write(f"- **Token Distribution**: Min: {report.min_tokens}, P25: {report.p25_tokens}, P75: {report.p75_tokens}, P95: {report.p95_tokens}, Max: {report.max_tokens}\n")
            f.write(f"- **Detected Anomalies**: {report.anomalies_count} ({(report.anomalies_count / report.total_chunks_evaluated) * 100:.2f}%)\n")
            f.write("\n---\n\n")

            f.write("## Deterministic Lexical Retrieval Benchmark (BM25)\n\n")
            f.write(f"- **Recall@1**: {report.recall_at_1 * 100:.1f}%\n")
            f.write(f"- **Recall@5**: {report.recall_at_5 * 100:.1f}%\n")
            f.write(f"- **Recall@10**: {report.recall_at_10 * 100:.1f}%\n")
            f.write(f"- **Mean Reciprocal Rank (MRR)**: {report.mrr:.3f}\n\n")

            f.write("| Query ID | Subject | First Relevant Rank | R@1 | R@5 | R@10 | Reciprocal Rank | Top Preview |\n")
            f.write("|----------|---------|---------------------|-----|-----|------|-----------------|-------------|\n")
            for r in report.retrieval_results:
                r1_str = "✅" if r.is_recall_at_1 else "❌"
                r5_str = "✅" if r.is_recall_at_5 else "❌"
                r10_str = "✅" if r.is_recall_at_10 else "❌"
                rank_str = str(r.rank_of_first_relevant) if r.rank_of_first_relevant else ">10"
                f.write(
                    f"| {r.query_id} | {r.target_subject} | {rank_str} | {r1_str} | {r5_str} | {r10_str} | {r.reciprocal_rank:.3f} | {r.top_preview[:60]}... |\n"
                )
            f.write("\n---\n\n")

            if report.anomalies:
                f.write("## Sample Anomalies Sampled\n\n")
                f.write("| Chunk ID | Issue Type | Tokens | Details | Source |\n")
                f.write("|----------|------------|--------|---------|--------|\n")
                for a in report.anomalies[:15]:
                    f.write(f"| `{a.chunk_id}` | `{a.issue_type}` | {a.token_count} | {a.details} | `{a.source_document}` p.{a.source_page} |\n")
            else:
                f.write("## Anomalies Sampled\n\n*No structural or contamination anomalies detected.*\n")
