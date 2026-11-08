# Phase 1 Test Report

Executed:

`./.venv/Scripts/python.exe -m pytest backend/tests/test_security_and_curriculum_access.py backend/tests/test_reviewer_portal_and_reconciliation.py backend/tests/test_database_isolation.py -q`

Result: **33 passed**, 3 deprecation warnings.

Frontend Vitest: **37 passed**, but logs unmocked relative API URL failures. Full backend collection remains blocked by missing `pymupdf` and `faiss` in the current virtual environment; it was not misrepresented as passing.
