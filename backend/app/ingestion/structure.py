import re
from typing import List, Optional, Tuple, Dict, Any
from backend.app.ingestion.schemas import (
    CleanedPage,
    ChapterCandidate,
    TopicCandidate,
    StructureConfidence,
    DetectionSource,
)


class StructureParser:
    """
    Deterministic curriculum structure detector.
    Analyzes page content and extracted table of contents to identify:
    - Chapter candidates (e.g. Chapter 1, Unit 1, Lesson 1)
    - Topic candidates (e.g. 1.1, 1.2, section headers)
    
    CRITICAL RESEARCH INTEGRITY RULE:
    NEVER invent fake topics. If no subsections are detected within a chapter,
    the topic candidate remains an explicit chapter-level primary topic
    or marked AMBIGUOUS / LOW_CONFIDENCE.
    """

    def __init__(self):
        # Chapter pattern matches
        self.chapter_patterns = [
            # "Chapter 1 Chemical Reactions and Equations 1" or "Chapter 1 : Title"
            re.compile(r"^(?:CHAPTER|UNIT|LESSON)\s*(\d+|[IVXLCDM]+)[\s:.\-]+([^\n\d]+?)(?:\s+\d+)?$", re.IGNORECASE),
            # "1. Chemical Reactions and Equations"
            re.compile(r"^(\d+)\.\s+([A-Z][A-Za-z0-9\s,\-–\(\)]+)$"),
            # Inverted NCERT style: "1CHAPTER" or "CHAPTER 1"
            re.compile(r"^(\d+)\s*CHAPTER$", re.IGNORECASE),
            re.compile(r"^CHAPTER\s*(\d+)$", re.IGNORECASE),
        ]

        # Topic/subsection pattern matches: e.g. "1.1 Chemical Equations", "2.3 What is a Base?"
        self.topic_pattern = re.compile(
            r"^(\d+)\.(\d+)\s+([A-Z][A-Za-z0-9\s,\-–\?\(\)\/]+)$"
        )

    def parse_structure(
        self,
        cleaned_pages: List[CleanedPage],
    ) -> List[ChapterCandidate]:
        """
        Extracts chapter and topic candidates from the sequence of cleaned pages.
        Attempts TOC-based extraction first. If TOC is absent or insufficient,
        falls back to page-by-page heading heuristics.
        """
        # 1. Attempt TOC detection in early pages (pages 1 to 25)
        toc_chapters = self._detect_toc_structure(cleaned_pages)
        if toc_chapters and len(toc_chapters) >= 2:
            # We found a viable TOC! Refine topic candidates within the page ranges
            self._refine_topics_from_pages(toc_chapters, cleaned_pages)
            return toc_chapters

        # 2. Fallback: Scan full book for chapter title patterns
        fallback_chapters = self._scan_chapters_from_pages(cleaned_pages)
        if fallback_chapters:
            self._refine_topics_from_pages(fallback_chapters, cleaned_pages)
            return fallback_chapters

        # 3. If no chapters detected at all, create a single unsegmented chapter
        # with LOW_CONFIDENCE to avoid failing or inventing structure
        return [
            ChapterCandidate(
                chapter_number=1,
                chapter_title="General Curriculum Content",
                start_pdf_page=1,
                end_pdf_page=cleaned_pages[-1].pdf_page_number if cleaned_pages else 1,
                confidence=StructureConfidence.LOW_CONFIDENCE,
                detection_method=DetectionSource.HEURISTIC,
                topics=[
                    TopicCandidate(
                        topic_order=1,
                        topic_title="General Content",
                        start_pdf_page=1,
                        end_pdf_page=cleaned_pages[-1].pdf_page_number if cleaned_pages else 1,
                        confidence=StructureConfidence.LOW_CONFIDENCE,
                        detection_method=DetectionSource.HEURISTIC,
                    )
                ],
            )
        ]

    def _detect_toc_structure(self, early_pages: List[CleanedPage]) -> List[ChapterCandidate]:
        """
        Inspects pages for 'CONTENTS' or 'TABLE OF CONTENTS' sections.
        Supports multi-page TOCs (e.g. First Flight, Maths) and tight numeric formatting.
        """
        chapters: List[ChapterCandidate] = []
        toc_pattern_ch = re.compile(
            r"^(?:CHAPTER|UNIT|LESSON)\s*(\d+|[IVXLCDM]+)[\s:.\-]+([^\n\d]+?)\s+(\d+)\s*$",
            re.IGNORECASE,
        )
        toc_pattern_num = re.compile(
            r"^(\d+)\.\s+([^\n\d]+?)\s+(\d+)\s*$"
        )
        # Handles tight numbers: "1. Real Numbers1", "2. Polynomials10"
        toc_pattern_tight = re.compile(
            r"^(\d+)\.\s+([A-Za-z\s,\-–\(\)]+?)(\d+)\s*$"
        )
        # Handles OCR corrupted numbers e.g. "’. Madam Rides the Bus 94" -> 7
        toc_pattern_special = re.compile(
            r"^([0-9\u2018\u2019\ufffd\x91\x92]+)\.\s+([^\n\d]+?)\s+(\d+)\s*$"
        )

        # First find where TOC begins
        in_toc = False
        toc_page_indices = []
        for idx, page in enumerate(early_pages[:25]):
            if not page.cleaned_text:
                continue
            text_upper = page.cleaned_text.upper()
            if "CONTENTS" in text_upper or "INDEX" in text_upper:
                in_toc = True
                toc_page_indices.append(idx)
            elif in_toc:
                # Often TOC spans 2-3 consecutive pages without repeating the title
                # Check if page has multiple chapter-like lines
                has_chapter_line = False
                for l in page.cleaned_text.split("\n"):
                    l_str = l.strip()
                    if (
                        toc_pattern_ch.match(l_str)
                        or toc_pattern_num.match(l_str)
                        or toc_pattern_tight.match(l_str)
                        or toc_pattern_special.match(l_str)
                    ):
                        has_chapter_line = True
                        break
                if has_chapter_line:
                    toc_page_indices.append(idx)
                else:
                    in_toc = False

        for idx in toc_page_indices:
            page = early_pages[idx]
            lines = page.cleaned_text.split("\n")
            for line in lines:
                line_clean = line.strip()
                m = (
                    toc_pattern_ch.match(line_clean)
                    or toc_pattern_num.match(line_clean)
                    or toc_pattern_tight.match(line_clean)
                )
                if m:
                    ch_num_str = m.group(1)
                    try:
                        ch_num = int(ch_num_str)
                    except ValueError:
                        ch_num = len(chapters) + 1

                    title = m.group(2).strip()
                    printed_page = int(m.group(3))

                    # Avoid duplicate chapter numbers
                    if not any(c.chapter_number == ch_num for c in chapters):
                        chapters.append(
                            ChapterCandidate(
                                chapter_number=ch_num,
                                chapter_title=title,
                                start_pdf_page=printed_page,
                                end_pdf_page=printed_page,
                                confidence=StructureConfidence.CONFIDENT,
                                detection_method=DetectionSource.TOC,
                                source_reference=f"TOC Entry: {line_clean}",
                                topics=[],
                            )
                        )
                    continue

                m2 = toc_pattern_special.match(line_clean)
                if m2:
                    raw_num = m2.group(1)
                    digits = re.findall(r"\d+", raw_num)
                    expected_num = (chapters[-1].chapter_number + 1) if chapters else 1
                    ch_num = int(digits[0]) if digits else expected_num
                    title = m2.group(2).strip()
                    printed_page = int(m2.group(3))

                    if not any(c.chapter_number == ch_num for c in chapters):
                        chapters.append(
                            ChapterCandidate(
                                chapter_number=ch_num,
                                chapter_title=title,
                                start_pdf_page=printed_page,
                                end_pdf_page=printed_page,
                                confidence=StructureConfidence.CONFIDENT,
                                detection_method=DetectionSource.TOC,
                                source_reference=f"TOC Entry: {line_clean}",
                                topics=[],
                            )
                        )

        # If TOC chapters were found, sort by chapter number and align page ranges
        if chapters:
            chapters.sort(key=lambda c: c.chapter_number)
            self._align_toc_chapters_to_pdf_pages(chapters, early_pages)

        return chapters

    def _align_toc_chapters_to_pdf_pages(
        self,
        chapters: List[ChapterCandidate],
        pages: List[CleanedPage],
    ):
        """
        Calibrates TOC printed page numbers to physical PDF page numbers by detecting
        where the first chapter actually appears, then offsets subsequent chapters.
        """
        if not chapters:
            return

        first_ch = chapters[0]
        # Search for first chapter title in early pages beyond TOC (pages 5 to 30)
        detected_offset = 0
        search_words = [w.lower() for w in first_ch.chapter_title.split() if len(w) > 3]

        for p in pages:
            if p.pdf_page_number > 5:
                p_text_lower = p.cleaned_text.lower()
                # If majority of words match
                matches = sum(1 for w in search_words if w in p_text_lower)
                if matches >= max(1, len(search_words) - 1):
                    detected_offset = p.pdf_page_number - first_ch.start_pdf_page
                    break

        # Apply offset to all chapters
        max_page = pages[-1].pdf_page_number if pages else 999
        for ch in chapters:
            ch.start_pdf_page = min(max_page, max(1, ch.start_pdf_page + detected_offset))

        for i in range(len(chapters)):
            if i < len(chapters) - 1:
                next_start = chapters[i + 1].start_pdf_page
                chapters[i].end_pdf_page = max(chapters[i].start_pdf_page, next_start - 1)
            else:
                chapters[i].end_pdf_page = max_page

    def _scan_chapters_from_pages(self, pages: List[CleanedPage]) -> List[ChapterCandidate]:
        """
        Scans pages sequentially for prominent chapter headings.
        """
        chapters: List[ChapterCandidate] = []
        heading_re = re.compile(r"^(?:CHAPTER|UNIT)\s*(\d+)[\s:\-]+([^\n]+)?$", re.IGNORECASE)
        inverted_re = re.compile(r"^(\d+)\s*CHAPTER$", re.IGNORECASE)

        for page in pages:
            if not page.cleaned_text:
                continue
            lines = [l.strip() for l in page.cleaned_text.split("\n") if l.strip()]
            for idx, line in enumerate(lines[:5]):  # Check first 5 lines of page
                m = heading_re.match(line)
                if m:
                    ch_num = int(m.group(1))
                    title = m.group(2) if m.group(2) else ""
                    if not title and idx + 1 < len(lines):
                        # Title might be on next line
                        title = lines[idx + 1]
                    title = title.strip() if title else f"Chapter {ch_num}"

                    # Avoid duplicates on consecutive pages
                    if not chapters or chapters[-1].chapter_number != ch_num:
                        if chapters:
                            chapters[-1].end_pdf_page = max(chapters[-1].start_pdf_page, page.pdf_page_number - 1)
                        chapters.append(
                            ChapterCandidate(
                                chapter_number=ch_num,
                                chapter_title=title,
                                start_pdf_page=page.pdf_page_number,
                                end_pdf_page=page.pdf_page_number,
                                confidence=StructureConfidence.CONFIDENT,
                                detection_method=DetectionSource.HEADING,
                                topics=[],
                            )
                        )
                    break
                
                m2 = inverted_re.match(line)
                if m2:
                    ch_num = int(m2.group(1))
                    # Title is usually the lines preceding or following
                    title = lines[0] if idx > 0 else (lines[idx + 1] if idx + 1 < len(lines) else f"Chapter {ch_num}")
                    if not chapters or chapters[-1].chapter_number != ch_num:
                        if chapters:
                            chapters[-1].end_pdf_page = max(chapters[-1].start_pdf_page, page.pdf_page_number - 1)
                        chapters.append(
                            ChapterCandidate(
                                chapter_number=ch_num,
                                chapter_title=title,
                                start_pdf_page=page.pdf_page_number,
                                end_pdf_page=page.pdf_page_number,
                                confidence=StructureConfidence.CONFIDENT,
                                detection_method=DetectionSource.HEADING,
                                topics=[],
                            )
                        )
                    break

        if chapters and pages:
            chapters[-1].end_pdf_page = pages[-1].pdf_page_number

        return chapters

    def _refine_topics_from_pages(
        self,
        chapters: List[ChapterCandidate],
        pages: List[CleanedPage],
    ):
        """
        Scans pages within each chapter's boundaries to find topic candidates.
        """
        page_map = {p.pdf_page_number: p for p in pages}

        for chapter in chapters:
            topics: List[TopicCandidate] = []
            current_topic: Optional[TopicCandidate] = None

            for p_num in range(chapter.start_pdf_page, chapter.end_pdf_page + 1):
                page = page_map.get(p_num)
                if not page or not page.cleaned_text:
                    continue

                lines = page.cleaned_text.split("\n")
                for line in lines:
                    line_str = line.strip()
                    m = self.topic_pattern.match(line_str)
                    if m:
                        sec_major = int(m.group(1))
                        sec_minor = int(m.group(2))
                        # Match section to chapter number if applicable
                        if sec_major == chapter.chapter_number or len(topics) == 0:
                            topic_title = m.group(3).strip()
                            # Finalize previous topic
                            if current_topic:
                                current_topic.end_pdf_page = max(current_topic.start_pdf_page, p_num - 1)
                                topics.append(current_topic)

                            current_topic = TopicCandidate(
                                topic_order=len(topics) + 1,
                                topic_title=f"{sec_major}.{sec_minor} {topic_title}",
                                start_pdf_page=p_num,
                                end_pdf_page=p_num,
                                confidence=StructureConfidence.CONFIDENT,
                                detection_method=DetectionSource.HEADING,
                            )

            if current_topic:
                current_topic.end_pdf_page = chapter.end_pdf_page
                topics.append(current_topic)

            # If no numbered topics were found, create one primary topic for the chapter
            if not topics:
                topics.append(
                    TopicCandidate(
                        topic_order=1,
                        topic_title=chapter.chapter_title,
                        start_pdf_page=chapter.start_pdf_page,
                        end_pdf_page=chapter.end_pdf_page,
                        confidence=StructureConfidence.CONFIDENT,
                        detection_method=chapter.detection_method,
                    )
                )

            chapter.topics = topics
