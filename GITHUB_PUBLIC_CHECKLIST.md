# GitHub Public Release Checklist

Use this checklist to prepare the repository for public publishing on GitHub.

---

## Phase 1: Secret Sanitization

- [x] Scan all files for API keys, tokens, connection strings
- [x] Confirm no hardcoded secrets in source code (`.py`, `.html`, `.js`)
- [x] Confirm no secrets in documentation files (`docs/*.md`, `README.md`)
- [x] Confirm no secrets in cache files (`backend/cache/*.json`)
- [x] Delete `temp_security_video.mp4` (generated download artifact)
- [ ] **Rotate all 12 live credentials in `.env`** (see `.env.example` for complete list)
- [ ] Verify `.env` is in `.gitignore` ✅

### Files Scanned

| File Path | Secrets Found | Action Taken |
|-----------|--------------|--------------|
| `.env` | **12 live secrets** | Added to `.gitignore` — **DO NOT COMMIT** |
| `docs/API_DOCUMENTATION.md` | None | Safe |
| `docs/CLAUDE.md` | None | Safe |
| `docs/DEPLOYMENT_GUIDE.md` | None (uses `"..."` placeholders) | Safe |
| `docs/IMPROVEMENT_SUGGESTIONS.md` | None | Safe |
| `docs/PROJECT_CONTEXT.md` | None | Safe |
| `docs/PROJECT_OVERVIEW.md` | None | Safe |
| `docs/REPOSITORY_ANALYSIS_REPORT.md` | None (warns about secrets) | Safe |
| `docs/SECURITY_ANALYSIS.md` | None | Safe |
| `docs/SYSTEM_ARCHITECTURE.md` | None | Safe |
| `docs/USER_FLOW.md` | None | Safe |
| `docs/DATABASE_DESIGN.md` | None | Safe |
| `docs/FOLDER_STRUCTURE.md` | None | Safe |
| `README.md` | None (warns about secrets) | Safe |
| `CHANGELOG.md` | None | Safe |
| `CONTRIBUTING.md` | None | Safe |
| `LICENSE.md` | None | Safe |
| `PROJECT_SHOWCASE.md` | None | Safe |
| `GITHUB_PUBLIC_CHECKLIST.md` | None | Safe |
| `main.py` | None (reads from env) | Safe |
| `backend/src/api/server.py` | None (reads from env) | Safe |
| `backend/src/api/telemetry.py` | None (reads from env) | Safe |
| `backend/src/graph/nodes.py` | None (reads from env) | Safe |
| `backend/src/graph/state.py` | None | Safe |
| `backend/src/graph/workflow.py` | None | Safe |
| `backend/src/services/cache_service.py` | None | Safe |
| `backend/src/services/video_indexer.py` | None (reads from env) | Safe |
| `backend/scripts/index_documents.py` | None (reads from env) | Safe |
| `frontend/index.html` | None | Safe |
| `pyproject.toml` | None | Safe |
| `uv.lock` | None | Safe |
| `backend/cache/*.json` | **YouTube URLs only** | Deleted (clean start) |

---

## Phase 2: Repository Structure

- [x] `README.md` — Professional, feature-rich, with Mermaid diagrams
- [x] `CONTRIBUTING.md` — Contribution guidelines
- [x] `LICENSE.md` — MIT License
- [x] `CHANGELOG.md` — Version history
- [x] `PROJECT_SHOWCASE.md` — Recruiter/hackathon showcase
- [x] `GITHUB_PUBLIC_CHECKLIST.md` — This checklist
- [x] `.env.example` — Template with placeholder values
- [ ] `.github/ISSUE_TEMPLATE/` — Issue templates (optional)
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` — PR template (optional)

---

## Phase 3: .gitignore Verification

- [x] `.env` — Environment secrets
- [x] `.venv/` — Virtual environment
- [x] `__pycache__/` — Python bytecode
- [x] `*.py[oc]` — Compiled Python
- [x] `build/`, `dist/`, `wheels/`, `*.egg-info` — Build artifacts
- [ ] `backend/cache/` — **ADD THIS** (cache is generated, not source)
- [ ] `backend/data/*.pdf` — **ADD THIS** (PDFs may be proprietary)
- [ ] `temp_*.mp4` — **ADD THIS** (downloaded temp videos)
- [ ] `.DS_Store` — macOS artifacts
- [ ] `*.pyc` — Python bytecode files

---

## Phase 4: Code Quality

- [ ] Add `pytest` configuration in `pyproject.toml`
- [ ] Add basic test structure: `tests/` directory
- [ ] Add Python type stubs or mypy configuration (optional)
- [ ] Add pre-commit hooks configuration (optional)
- [ ] Verify `uv.lock` is reproducible (test `uv sync --frozen`)

---

## Phase 5: Documentation Final Check

- [ ] All `docs/*.md` files reviewed for sensitive content
- [ ] No internal URLs, IPs, or infrastructure details exposed
- [ ] No Azure resource names, subscription IDs, or account GUIDs
- [ ] All environment variable references use `your_*` placeholders
- [ ] `docs/REPOSITORY_ANALYSIS_REPORT.md` reviewed for sensitive findings (exposed secrets warning is appropriate — it warns without revealing values)

---

## Phase 6: Git History Cleanup

- [ ] Check git history for accidentally committed secrets:
  ```bash
  git log --oneline -20
  git diff HEAD~1 -- .env  # Check if .env was ever committed
  ```
- [ ] If secrets were committed in history, use `git filter-branch` or `bfg` to purge
- [ ] Force push cleaned history

---

## Phase 7: GitHub Repository Settings

- [ ] Enable **Dependabot** alerts
- [ ] Enable **Secret scanning**
- [ ] Set **default branch** to `main`
- [ ] Require **pull request reviews** before merge
- [ ] Add **branch protection rules** for `main`
- [ ] Add **Repository Topics**: `security`, `ai`, `threat-detection`, `national-security`, `llm`, `azure`, `fastapi`
- [ ] Set **License** to MIT in repo settings
- [ ] Add **Repository description** and **website URL** (if applicable)

---

## Phase 8: Pre-Publish Test

```bash
# Clone to a fresh directory
cd /tmp
git clone /path/to/national-security-shield.git test-publish
cd test-publish

# Verify no secrets
Get-ChildItem -Recurse -File | Select-String -Pattern "gsk_", "lsv2_", "AccountKey=" | ForEach-Object { Write-Host "SECRET FOUND in $($_.Path):$($_.LineNumber)" }

# Verify build
uv sync --frozen

# Verify env template
if (Test-Path .env) { Write-Host "ERROR: .env is present!" } else { Write-Host "OK: .env is absent" }
if (Test-Path .env.example) { Write-Host "OK: .env.example is present" }

# List all files to verify clean state
Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\\.venv' } | Select-Object FullName
```

---

## Summary: Files by Visibility

### ✅ Safe to Publish (no secrets)

| File | Notes |
|------|-------|
| `main.py` | CLI entry point |
| `pyproject.toml` | Dependencies |
| `README.md` | Project overview |
| `CHANGELOG.md` | Version history |
| `CONTRIBUTING.md` | Contribution guide |
| `LICENSE.md` | MIT License |
| `PROJECT_SHOWCASE.md` | Recruiter showcase |
| `GITHUB_PUBLIC_CHECKLIST.md` | This checklist |
| `docs/*.md` (12 files) | All documentation (no secrets) |
| `backend/src/**/*.py` (8 files) | All source code (reads from env) |
| `backend/scripts/*.py` (1 file) | Utility script |
| `frontend/index.html` | Web dashboard |
| `.gitignore` | Git ignore rules |
| `.python-version` | Python version |
| `.env.example` | Template (placeholder values) |
| `uv.lock` | Lock file |

### 🚫 Must Stay Private (never commit)

| File | Reason |
|------|--------|
| `.env` | **Contains 12 live API keys and secrets** |

### 🗑️ Deleted Before Publish

| File | Reason |
|------|--------|
| `temp_security_video.mp4` | Downloaded video artifact (4 MB) |
| `backend/cache/*.json` | Generated scan results (clean state) |

### ✏️ Requires Action Before Publish

| Item | Action |
|------|--------|
| All 12 secrets in `.env` | **Rotate immediately** |
| Git commit history | Check for prior `.env` commits |
| GitHub repo settings | Enable security features |
