"""
CLI script to run vector diagram extraction for NEET UG 2021 Booklet M4.

Outputs:
- PNG assets in backend/static/assets/diagrams/neet_2021/
- Machine-readable manifest in data/processed/neet_2021_diagram_manifest.json
- HTML review contact sheet in data/processed/neet_2021_diagram_contact_sheet.html

Milestone 5.7.
"""

import sys
import os
import argparse
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ingestion.vector_diagram_extractor import (
    VectorDiagramExtractor,
    NEET_2021_M4_CONFIGS,
    VectorExtractionError,
)

EXPECTED_NEET_2021_PDF_HASH = "e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a"


def main():
    parser = argparse.ArgumentParser(description="Extract NEET 2021 vector diagrams and graphical options.")
    parser.add_argument(
        "--pdf-path",
        default="GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf",
        help="Path to authoritative NEET 2021 PDF",
    )
    parser.add_argument(
        "--output-dir",
        default="backend/static/assets/diagrams/neet_2021",
        help="Output directory for rasterized PNG assets",
    )
    parser.add_argument(
        "--manifest-path",
        default="data/processed/neet_2021_diagram_manifest.json",
        help="Path for machine-readable JSON manifest",
    )
    parser.add_argument(
        "--contact-sheet-path",
        default="data/processed/neet_2021_diagram_contact_sheet.html",
        help="Path for visual HTML contact sheet",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing assets if hashes differ",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="PyMuPDF render scale matrix factor (default: 2.0 = 144 DPI)",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=4.0,
        help="Padding in PDF points around diagram bbox (default: 4.0 pt)",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("diagram_extractor")

    logger.info("Initializing VectorDiagramExtractor...")
    extractor = VectorDiagramExtractor(
        output_base_dir=args.output_dir,
        render_scale=args.scale,
        padding_pts=args.padding,
    )

    try:
        logger.info(f"Extracting visual assets from {args.pdf_path}...")
        records = extractor.extract_all(
            pdf_path=args.pdf_path,
            target_configs=NEET_2021_M4_CONFIGS,
            expected_pdf_sha256=EXPECTED_NEET_2021_PDF_HASH,
            overwrite=args.overwrite,
        )

        extracted_count = sum(1 for r in records if r.extraction_status == "EXTRACTED")
        failed_count = sum(1 for r in records if r.extraction_status == "FAILED")
        logger.info(f"Extraction finished: {extracted_count} extracted, {failed_count} failed out of {len(records)} targets.")

        logger.info(f"Generating manifest at {args.manifest_path}...")
        extractor.generate_manifest(records, args.manifest_path)

        logger.info(f"Generating contact sheet at {args.contact_sheet_path}...")
        extractor.generate_contact_sheet(records, args.contact_sheet_path)

        if failed_count > 0:
            logger.error(f"Extraction incomplete: {failed_count} targets failed!")
            sys.exit(1)

        logger.info("Vector diagram extraction and manifest generation completed successfully!")
        sys.exit(0)

    except VectorExtractionError as e:
        logger.error(f"Vector extraction failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error during extraction: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
