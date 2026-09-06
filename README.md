# DevGuard 🛡️

**DevGuard** is a local-first, autonomous Python security auditor and static analysis agent. Powered by AST parsing and Gemini 2.5-Flash, it scans codebases for vulnerabilities, anti-patterns, and performance bottlenecks—offering interactive CLI feedback and containerized deployment options.

---

## Key Features

* **AST-Powered Parsing**: Scans target source trees to construct precise Abstract Syntax Trees without executing untrusted code.
* **Context Retrieval**: Filters relevant code chunks, imports, and definitions for LLM security analysis.
* **Autonomous AI Audit**: Integrates `google-genai` (Gemini 2.5-Flash) to evaluate code safety, secrets, injection risks, and PEP 8 compliance.
* **Rich Terminal UI**: Delivers formatted security findings directly to the console using `rich`.
* **Containerized Execution**: Ships with a lightweight Docker image for isolated, cross-platform security analysis.

---

## Project Architecture

```text
devguard-agent/
├── src/
│   └── devguard/
│       ├── __init__.py
│       ├── agent.py        # Gemini API integration & prompt engine
│       ├── cli.py          # Entry point & Rich TUI rendering
│       ├── parser.py       # Python AST analysis & file parsing
│       └── retriever.py    # Codebase context extraction engine
├── tests/
│   ├── test_parser.py     # Unit tests for AST parsing logic
│   └── test_retriever.py  # Unit tests for code chunk extraction
├── Dockerfile              # Production container specification
├── pyproject.toml          # Package metadata & CLI entry points
└── README.md