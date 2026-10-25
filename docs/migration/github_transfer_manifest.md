# EduNavika — Complete GitHub & External Drive Transfer Manifest

## 1. Overview & Destination Architecture

This manifest specifies the complete inventory, classification, and migration path for transferring the **EduNavika** project from the source laptop to a new target workstation:

- **Destination Hardware**: Windows 11 64-bit, 16 GB RAM, NVIDIA GPU.
- **Source Repository**: `https://github.com/tkacha467/EduNavika.git` (Branch: `master`).
- **Transfer Topology**:
  - **GitHub**: Source code, tests, documentation, configuration templates, deterministic schemas, and lightweight static diagram assets ($\le 500\text{ KB}$).
  - **External Drive**: Canonical SQLite database (`edunavika.db`), official high-resolution textbook PDFs (`GSEB-Dataset/`), raw model weights (`models/*.gguf`), and FAISS vector indices.
  - **Package Registries (PyPI / npm)**: Regenerable virtual environments (`.venv/`) and frontend packages (`frontend/node_modules/`).

---

## 2. Comprehensive Asset Classification Matrix

Every file and directory in the project is explicitly categorized into one of four transfer classes:

| Class | Description | Destination / Handling | Example Paths |
| :---: | :--- | :--- | :--- |
| **A** | **GitHub Tracked** | Source code, test suites, architecture docs, config templates, lightweight static assets. | `backend/app/`, `frontend/src/`, `backend/tests/`, `backend/static/`, `docs/`, `requirements.txt`, `.env.example` |
| **B** | **External Drive Transfer** | Canonical local database, official high-volume PDF corpus, reference answer keys. | `edunavika.db`, `GSEB-Dataset/` (1.2 GB+), `docs/reference/Notice_20211101205130.pdf` |
| **C** | **Regenerable / Build** | Virtual environments, node modules, build bundles, test caches. | `.venv/`, `frontend/node_modules/`, `frontend/dist/`, `.pytest_cache/` |
| **D** | **Restricted / Excluded** | Live API credentials, unencrypted secrets, machine-specific OS files. | `.env`, `.DS_Store`, `__MACOSX/`, `*.db-wal`, `*.db-shm` |

---

## 3. Class A: Files Committed and Tracked on GitHub

These files are committed directly to the Git repository and will be cloned automatically:

1. **Backend Application (`backend/app/`)**:
   - `core/`: Database connections (`database.py`), settings schema (`config.py`), security utilities.
   - `models/`: Canonical curriculum models (`core_models.py`), competitive exam models (`competitive_models.py`).
   - `schemas/`: Pydantic validation contracts for attempts, revisions, curriculum, and competitive exams.
   - `api/v1/`: FastAPI routers, auth endpoints, curriculum endpoints, and competitive CBT exam endpoints.
   - `services/`: Ingestion services, answer key reconciliation, competitive assessment service, adaptive practice.
   - `ingestion/`: Text scanner, competitive paper parser, and vector diagram extractor (`vector_diagram_extractor.py`).
2. **Frontend Application (`frontend/`)**:
   - `src/`: TypeScript application components, CBT test views (`StudentViews.ts`), exam services (`competitiveService.ts`), layout navigation (`AppShell.ts`), router (`router.ts`).
   - Build configs: `vite.config.ts`, `tsconfig.json`, `package.json`, `package-lock.json`.
3. **Database Migrations (`backend/alembic/`)**:
   - Alembic environment (`env.py`), revision scripts (up to head `a1b2c3d4e5f6` / `f1e2d3c4b5a6`).
4. **Test Suites (`backend/tests/`)**:
   - 480+ unit and integration tests covering curriculum integrity, CBT gates, vector diagram extraction, and database isolation.
5. **Static Assets (`backend/static/`)**:
   - 41 extracted lossless PNG diagrams for NEET UG 2021 (`backend/static/assets/diagrams/neet_2021/`).
6. **Documentation & Processed Manifests**:
   - `docs/`: Milestone specifications (5.1 through 5.7), curriculum models, architecture diagrams.
   - `data/processed/`: Machine-readable audit manifests (`neet_2021_diagram_manifest.json`, `neet_2021_quality_audit.json`, HTML contact sheet).
7. **Environment Templates & Dependencies**:
   - `.env.example`, `requirements.txt`, `.gitignore`.

---

## 4. Class B: External Drive Transfer (Large & Authoritative Assets)

These assets must be copied to the new workstation using an external SSD/USB drive. They are intentionally excluded from GitHub to maintain repository speed, respect copyright licensing, and prevent binary database corruption.

### 1. Canonical Database
- **Relative Path**: `edunavika.db`
- **File Size**: 4,882,432 bytes (~4.65 MB)
- **SHA-256**: `97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`
- **Restoration Target on New Laptop**: `<repo_root>/edunavika.db`
- **Alternative Initialization**: If starting fresh, run `alembic upgrade head` and `backend.app.services.curriculum_question_bank.sync_canonical_questions_to_db()`.

### 2. Official Source Datasets (Textbooks & Papers)
- **Directory**: `GSEB-Dataset/`
- **Total Footprint**: ~1.3 GB (contains Gujarati & English medium textbooks for Classes 10, 11, 12, plus JEE/NEET PYQs)
- **Critical File for Milestone 5.7**:
  - `GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf` (Booklet M4)
  - Size: 947,343 bytes
  - SHA-256: `e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a`
- **Restoration Target on New Laptop**: `<repo_root>/GSEB-Dataset/`

### 3. Official Answer Key Ground Truth
- **File**: `docs/reference/Notice_20211101205130.pdf`
- **Size**: 216,680 bytes
- **SHA-256**: `838e0ba080eb6b9639f12a1dcfb7f36cd8fe80dd5be11ee0be6d725e4c6f3ca9`
- **Restoration Target on New Laptop**: `<repo_root>/docs/reference/Notice_20211101205130.pdf`

### 4. Optional On-Device Model Weights
- **Directory**: `models/` (Optional GGUF weights, e.g. `qwen2.5-0.5b-instruct-q4_k_m.gguf`, ~350 MB)
- **Handling**: Transfer via external drive or download from Hugging Face if local SLM inference is required.

---

## 5. Class C: Regenerable Artifacts (Install On-Demand)

Do not transfer these folders; they should be cleanly installed on the new Windows 11 machine:
- Python virtual environment: `.venv/` (recreate with Python 3.11: `python -m venv .venv`).
- Node packages: `frontend/node_modules/` (recreate with Node 20+: `npm ci`).
- Vite bundle: `frontend/dist/` (recreate with `npm run build`).
- Python bytecache: `__pycache__/`, `*.pyc`.
- Pytest cache: `.pytest_cache/`.

---

## 6. Class D: Excluded & Sensitive Files

- Real `.env` containing production API keys or tokens.
- SQLite temporary write-ahead logs (`edunavika.db-wal`, `edunavika.db-shm`).
- macOS metadata artifacts (`.DS_Store`, `__MACOSX/`).
- Local backup snapshots (`backups/`).

---

## 7. Destination Laptop Step-by-Step Restoration Procedure

Follow these exact PowerShell commands on the new Windows 11 machine:

### Step 1: Install System Prerequisites
Ensure the following tools are installed via `winget` or official installers:
```powershell
# 1. Install Git
winget install --id Git.Git -e --source winget

# 2. Install Python 3.11 (Recommended version matching current stack)
winget install --id Python.Python.3.11 -e --source winget

# 3. Install Node.js (LTS v20 or v22)
winget install --id OpenJS.NodeJS.LTS -e --source winget
```

### Step 2: Clone Repository and Verify Branch
```powershell
# Clone to preferred workspace directory
git clone https://github.com/tkacha467/EduNavika.git
cd EduNavika

# Check out master and verify head commit
git checkout master
git rev-parse HEAD
# Expected output: 8331a892a51d96bf32489a008f8602a8e25da7b7 (or latest migration commit)
```

### Step 3: Restore External Assets from External Drive
Assuming external drive is mounted at `E:\`:
```powershell
# 1. Restore canonical database
Copy-Item "E:\EduNavika-Transfer\edunavika.db" -Destination ".\edunavika.db"

# 2. Restore GSEB dataset
Copy-Item -Recurse "E:\EduNavika-Transfer\GSEB-Dataset" -Destination ".\GSEB-Dataset"

# 3. Restore reference answer key
New-Item -ItemType Directory -Force -Path ".\docs\reference"
Copy-Item "E:\EduNavika-Transfer\Notice_20211101205130.pdf" -Destination ".\docs\reference\"
```

### Step 4: Set Up Python Backend Environment
```powershell
# Create fresh virtual environment with Python 3.11
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Set Up Frontend Environment
```powershell
cd frontend
npm ci
npm run build
cd ..
```

### Step 6: Create Environment Configuration
```powershell
# Copy example configuration template
Copy-Item .env.example .env
```

### Step 7: Verify Asset Integrity & Smoke Tests
```powershell
# 1. Verify NEET 2021 source PDF hash
Get-FileHash -Algorithm SHA256 ".\GSEB-Dataset\Dataset\Dataset\Neet\neet-2021.pdf"
# Expected: E9ACDFB29DFCFFA3A186819F7336330AF4CE51855990D1081C78637B338587A

# 2. Verify Canonical Database hash
Get-FileHash -Algorithm SHA256 ".\edunavika.db"
# Expected: 97F760B8CFA3BC22D632700E15B494013DFCA2FA2200CEBD56F80BA9934CEB01

# 3. Run Vector Diagram Extractor test suite
pytest backend/tests/test_vector_diagram_extractor.py -v

# 4. Run Core Competitive Ingestion Gate test suite
pytest backend/tests/test_production_ingestion_gate.py -v
```

### Step 8: Launch Application
```powershell
# Terminal 1: Start FastAPI Backend Server (runs on http://127.0.0.1:8000)
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start Vite Frontend Dev Server (runs on http://localhost:5173)
cd frontend
npm run dev
```

---

## 8. Verification Checklist for Destination Workstation

- [ ] `git status` reports clean working directory.
- [ ] `python -m pip list` confirms `fastapi`, `pymupdf`, `sqlalchemy`, `alembic` installed.
- [ ] `pytest backend/tests/test_vector_diagram_extractor.py` passes 12/12 tests.
- [ ] `http://127.0.0.1:8000/health` returns `{"status":"healthy","service":"EduNavika API","version":"1.0.0"}`.
- [ ] `http://127.0.0.1:8000/docs` displays Swagger UI with competitive and curriculum endpoints.
- [ ] `http://localhost:5173` loads Student CBT interface and Previous-Year Papers dashboard.
- [ ] Visual diagrams display cleanly in browser without broken image icons.
