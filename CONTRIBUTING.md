# Contributing to National Security Shield

Thank you for your interest in contributing to National Security Shield! This project aims to build AI-powered threat detection for national security applications.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Issues

- **Security vulnerabilities:** Email maintainers directly — do not open a public issue
- **Bug reports:** Include steps to reproduce, expected behavior, actual behavior, and environment details
- **Feature requests:** Describe the feature, its use case, and how it aligns with the project vision

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/national-security-shield.git
cd national-security-shield

# Create virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Fill in your Azure and Groq credentials

# Index knowledge base documents
uv run python backend/scripts/index_documents.py

# Start development server
uvicorn backend.src.api.server:app --reload --port 8000
```

### Project Structure

```
national-security-shield/
├── main.py                    # CLI entry point
├── backend/
│   ├── src/
│   │   ├── api/               # FastAPI REST endpoints
│   │   ├── graph/             # LangGraph workflow (DAG)
│   │   └── services/          # Business logic (cache, video indexer)
│   ├── scripts/               # Utility scripts
│   ├── data/                  # Knowledge base PDFs (gitignored if large)
│   └── cache/                 # Scan result cache (gitignored)
├── frontend/                  # Web dashboard
│   └── index.html
└── docs/                      # Documentation
```

### Pull Request Process

1. **Fork** the repository and create a feature branch from `main`
2. **Run existing tests** (when available): `pytest`
3. **Add tests** for new functionality
4. **Update documentation** in `docs/` for any changes
5. **Ensure no secrets** are committed — check for API keys, tokens, connection strings
6. **Create a pull request** with a clear description of changes

### Coding Standards

- **Python 3.13+** — use modern Python features
- **Type hints** — annotate all function signatures
- **Docstrings** — document purpose, parameters, and return values
- **No hardcoded secrets** — all credentials from environment variables
- **No debug/test files** — clean up before committing
- **Follow existing patterns** — mimic the code style of the module you're modifying

### Commit Messages

Use conventional commits:
```
feat: add Instagram video support
fix: handle Azure Video Indexer timeout
docs: update API documentation
security: rotate exposed credentials
refactor: extract cache service interface
test: add unit tests for threat analysis
```

### Security Notes

- Never commit `.env` files or any file containing API keys
- Never hardcode credentials in source code
- Run `git diff --staged` before committing to check for secrets
- Report security issues privately to maintainers
- Use environment variables for all configuration

## Getting Help

- Check existing documentation in `docs/`
- Open a GitHub Discussion for questions
- Tag maintainers for urgent issues

## Future Roadmap

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for the full roadmap and priority features.
