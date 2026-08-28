# Multi-Agent Psychology

MVP for structured psychological case analysis through multiple theoretical perspectives.

## What this MVP does
- Loads a JSON case from `input/`
- Produces independent viewpoints for psychology schools
- Runs a configurable number of critique rounds
- Writes an immutable run log and a final report
- Supports `analysis`, `consulting`, or `both` output modes

This first version uses deterministic, transparent agent stubs so that the workflow can be tested without model credentials. Replace `PerspectiveAgent` with an LLM-backed provider in the next iteration.

## Quick start
```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
python -m multi_agent_psychology.cli run input/example_case.json
pytest
```

## Repository layout
- `config/default.json` — workflow, agents, and output configuration
- `input/` — case files submitted for analysis
- `src/multi_agent_psychology/` — orchestrator and domain model
- `outputs/logs/` — per-run research/debate record
- `outputs/reports/` — final analysis and consulting reports
- `tests/` — workflow tests

## Case format
```json
{
  "case_id": "career-burnout-001",
  "title": "High-performing employee burnout",
  "narrative": "…",
  "questions": ["What patterns should be explored?"],
  "mode": "both"
}
```

> Educational workflow only. The system must not diagnose, replace licensed care, or provide emergency guidance.
