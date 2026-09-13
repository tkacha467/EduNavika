import re
import hashlib
from typing import List, Dict, Any, Optional

from backend.app.ingestion.schemas import (
    CleanedPage,
    ChapterCandidate,
    TopicCandidate,
    ContentChunk,
    DocumentIdentity,
)
from backend.app.ingestion.math.quality_gate import MathQualityGate


class StructureAwareChunker:
    """
    Performs structure-aware deterministic chunking on cleaned textbook pages.
    - Target: ~500 to 800 tokens (~2000 to 3200 characters)
    - Boundaries respected: Headings, paragraphs, definitions, examples, formulas, activities
    - Preserves exact source traceability: document_id, pdf_page_start, pdf_page_end, chapter, topic
    - Generates reproducible, deterministic chunk IDs: chk_<sha256[:16]>
    - Content types classified conservatively: TEXT, EXAMPLE, DEFINITION, FORMULA, EXPLANATION
    - Validates mathematical integrity via MathQualityGate
    """

    def __init__(
        self,
        min_target_tokens: int = 400,
        max_target_tokens: int = 850,
        approx_chars_per_token: int = 4,
        math_quality_gate: Optional[MathQualityGate] = None,
    ):
        self.min_target_chars = min_target_tokens * approx_chars_per_token  # ~1600 chars
        self.max_target_chars = max_target_tokens * approx_chars_per_token  # ~3400 chars
        self.chars_per_token = approx_chars_per_token
        self.math_quality_gate = math_quality_gate or MathQualityGate()

    def chunk_document(
        self,
        doc_identity: DocumentIdentity,
        cleaned_pages: List[CleanedPage],
        chapters: List[ChapterCandidate],
    ) -> List[ContentChunk]:
        """
        Chunks the document page-by-page adhering to chapter and topic boundaries.
        """
        page_dict = {p.pdf_page_number: p for p in cleaned_pages}
        chunks: List[ContentChunk] = []
        chunk_counter = 1

        for chapter in chapters:
            for topic in chapter.topics:
                topic_chunks = self._chunk_topic(
                    doc_identity=doc_identity,
                    chapter=chapter,
                    topic=topic,
                    page_dict=page_dict,
                    start_chunk_index=chunk_counter,
                )
                chunks.extend(topic_chunks)
                chunk_counter += len(topic_chunks)

        return chunks

    def _chunk_topic(
        self,
        doc_identity: DocumentIdentity,
        chapter: ChapterCandidate,
        topic: TopicCandidate,
        page_dict: Dict[int, CleanedPage],
        start_chunk_index: int,
    ) -> List[ContentChunk]:
        chunks: List[ContentChunk] = []
        current_paras: List[str] = []
        current_char_count = 0
        current_page_start: Optional[int] = None
        current_page_end: Optional[int] = None
        chunk_idx = start_chunk_index

        for page_num in range(topic.start_pdf_page, topic.end_pdf_page + 1):
            cleaned_page = page_dict.get(page_num)
            if not cleaned_page or not cleaned_page.cleaned_text.strip():
                continue

            page_paras = [p.strip() for p in cleaned_page.cleaned_text.split("\n\n") if p.strip()]

            for para in page_paras:
                para_len = len(para)

                if current_char_count + para_len > self.max_target_chars and current_paras:
                    # Seal current chunk
                    chunk = self._create_chunk(
                        doc_identity=doc_identity,
                        chapter=chapter,
                        topic=topic,
                        text="\n\n".join(current_paras),
                        page_start=current_page_start or page_num,
                        page_end=current_page_end or page_num,
                        chunk_index=chunk_idx,
                    )
                    chunks.append(chunk)
                    chunk_idx += 1

                    # Reset accumulators
                    current_paras = [para]
                    current_char_count = para_len
                    current_page_start = page_num
                    current_page_end = page_num
                else:
                    current_paras.append(para)
                    current_char_count += para_len
                    if current_page_start is None:
                        current_page_start = page_num
                    current_page_end = page_num

        # Seal final remaining chunk if any content accumulated
        if current_paras:
            chunk = self._create_chunk(
                doc_identity=doc_identity,
                chapter=chapter,
                topic=topic,
                text="\n\n".join(current_paras),
                page_start=current_page_start or topic.start_pdf_page,
                page_end=current_page_end or topic.end_pdf_page,
                chunk_index=chunk_idx,
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        doc_identity: DocumentIdentity,
        chapter: ChapterCandidate,
        topic: TopicCandidate,
        text: str,
        page_start: int,
        page_end: int,
        chunk_index: int,
    ) -> ContentChunk:
        # Deterministic chunk ID hash based on document, chapter, topic, page range, and content
        hash_seed = f"{doc_identity.document_id}_{chapter.chapter_number}_{topic.topic_order}_{page_start}_{page_end}_{text.strip()}"
        chunk_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:16]
        chunk_id = f"chk_{chunk_hash}"

        approx_tokens = max(1, len(text) // self.chars_per_token)
        content_type = self._classify_content_type(text)

        # Scrutinize mathematical integrity
        math_val = self.math_quality_gate.validate_chunk(text, chunk_id=chunk_id)

        heading_path = f"Standard {doc_identity.standard} > {doc_identity.subject} > Chapter {chapter.chapter_number}: {chapter.chapter_title} > {topic.topic_title}"

        return ContentChunk(
            chunk_id=chunk_id,
            document_id=doc_identity.document_id,
            pdf_page_start=page_start,
            pdf_page_end=page_end,
            printed_page_start=None,
            printed_page_end=None,
            source_file=doc_identity.relative_path,
            content_type=content_type,
            chunk_index=chunk_index,
            text=text,
            approx_token_count=approx_tokens,
            heading_path=heading_path,
            section_title=topic.topic_title,
            extraction_method="pypdf",
            quality_status="EXTRACTED",
            metadata={
                "standard": doc_identity.standard,
                "subject": doc_identity.subject,
                "chapter_number": chapter.chapter_number,
                "chapter_title": chapter.chapter_title,
                "topic_order": topic.topic_order,
                "topic_title": topic.topic_title,
                "math_detected": math_val.has_math,
                "math_validity_status": math_val.status,
                "math_issues": math_val.detected_issues,
                "math_confidence": math_val.confidence_score,
            },
        )

    def _classify_content_type(self, text: str) -> str:
        """
        Conservative deterministic classification using domain patterns.
        Defaults to TEXT if uncertain.
        """
        lower = text.lower()
        if re.search(r"\b(example\s+\d+|solution\s*:)", lower):
            return "EXAMPLE"
        if re.search(r"\b(definition\s*:|is defined as\b|defined as follows)", lower):
            return "DEFINITION"
        if re.search(r"\b(formula\s*:|\b[a-z]\s*=\s*[a-z0-9\+\-\*\/]+\b|equation\s+\d+)", lower):
            return "FORMULA"
        if re.search(r"\b(activity\s+\d+|step\s+1\b|procedure\s*:)", lower):
            return "EXPLANATION"
        return "TEXT"
