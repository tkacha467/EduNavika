# Phase 1.2 Dependency Reliability

`requirements.txt` declares `pymupdf>=1.24.0` and `faiss-cpu`, while code imports `pymupdf` and `faiss`. The current virtual environment cannot import either package, blocking eight backend test modules at collection. CPU FAISS is the appropriate declared dependency; no GPU dependency is necessary.

Before claiming a repair, recreate a clean environment from pinned, platform-compatible dependency versions and execute the full suite. The repository currently has no lock file proving reproducibility.
