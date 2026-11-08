# Phase 1.3G Dependency Reliability

Full backend collection: 453 tests discovered and 9 collection errors. PyMuPDF imports fail in six modules, FAISS imports fail in three, and the obsolete in-memory security-test import fails. The active environment has neither `pymupdf` nor `faiss` despite declarations in `requirements.txt`.
