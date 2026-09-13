import re
import unicodedata
from typing import List, Optional, Tuple
from backend.app.ingestion.schemas import ExtractedPage, CleanedPage, PageQualityStatus


class DeterministicCleaner:
    """
    Applies deterministic, lossless, semantic-preserving cleaning to extracted PDF page text.
    - Unicode NFKC normalization
    - Line-break and hyphenated word repair
    - Whitespace normalization
    - Conservative header and footer suppression without destroying source context
    - Strictly preserves raw text alongside cleaned text for auditability
    """

    def __init__(
        self,
        suppress_headers_footers: bool = True,
        header_patterns: Optional[List[str]] = None,
        footer_patterns: Optional[List[str]] = None,
    ):
        self.suppress_headers_footers = suppress_headers_footers
        # Default header/footer heuristic patterns in GSEB textbooks
        self.header_patterns = header_patterns or [
            r"^(?:SCIENCE|MATHEMATICS|SOCIAL SCIENCE|ENGLISH|PHYSICS|CHEMISTRY|BIOLOGY)\s*$",
            r"^(?:STANDARD|STD\.?)\s*(?:9|10|11|12|IX|X|XI|XII)\b.*$",
        ]
        self.footer_patterns = footer_patterns or [
            r"^\d+\s*$",  # Page number on its own line
            r"^(?:Page|PAGE)\s*\d+\s*(?:of\s*\d+)?$",
            r"^.*(?:GSEB|Gujarat State Board of School Textbooks).*$",
        ]

    def clean_text(self, text: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Cleans a page text block and returns (cleaned_text, removed_header, removed_footer).
        """
        if not text or not text.strip():
            return "", None, None

        # 1. Decode font glyph escape sequences (e.g. /G83/G111 -> So) found in some GSEB PDFs
        def _safe_chr(match):
            val = int(match.group(1))
            return chr(val) if 0 <= val < 0x110000 else match.group(0)

        text = re.sub(r"/G(\d+)", _safe_chr, text)

        # 2. Unicode NFKC normalization
        normalized = unicodedata.normalize("NFKC", text)

        # 3. Normalize Windows/Mac line endings to \n
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 3. Line-by-line inspection for headers and footers
        lines = [line.strip() for line in normalized.split("\n")]
        # Filter out purely blank lines at top and bottom
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()

        if not lines:
            return "", None, None

        removed_header = None
        removed_footer = None

        if self.suppress_headers_footers:
            # Check if first line matches known header pattern or is very short book title
            if lines:
                first_line = lines[0]
                for pat in self.header_patterns:
                    if re.match(pat, first_line, re.IGNORECASE):
                        removed_header = lines.pop(0)
                        break

            # Check if last line matches known footer pattern
            if lines:
                last_line = lines[-1]
                for pat in self.footer_patterns:
                    if re.match(pat, last_line, re.IGNORECASE):
                        removed_footer = lines.pop()
                        break

        # 4. Repair hyphenated line breaks: e.g. "compo-\nsition" -> "composition"
        # We join hyphen at the end of a line followed by lowercase character
        repaired_lines: List[str] = []
        i = 0
        while i < len(lines):
            curr_line = lines[i]
            if curr_line.endswith("-") and i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line starts with lowercase letter, join them
                if next_line and next_line[0].islower():
                    repaired_lines.append(curr_line[:-1] + next_line)
                    i += 2
                    continue
            repaired_lines.append(curr_line)
            i += 1

        # 5. Clean each line: normalize internal spaces while preserving lines
        cleaned_lines: List[str] = []
        for line in repaired_lines:
            line_clean = re.sub(r"[ \t]+", " ", line).strip()
            cleaned_lines.append(line_clean)

        # Remove consecutive multiple blank lines
        final_lines: List[str] = []
        for line in cleaned_lines:
            if not line and final_lines and not final_lines[-1]:
                continue
            final_lines.append(line)

        cleaned_text = "\n".join(final_lines)

        return cleaned_text, removed_header, removed_footer

    def clean_page(self, page: ExtractedPage) -> CleanedPage:
        """
        Cleans an ExtractedPage into a CleanedPage while keeping raw data untouched.
        """
        cleaned_text, removed_header, removed_footer = self.clean_text(page.raw_text)

        return CleanedPage(
            document_id=page.document_id,
            pdf_page_number=page.pdf_page_number,
            printed_page_number=page.printed_page_number,
            cleaned_text=cleaned_text,
            quality_status=page.quality_status,
            removed_header=removed_header,
            removed_footer=removed_footer,
        )
