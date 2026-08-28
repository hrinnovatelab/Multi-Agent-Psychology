from __future__ import annotations

import shutil
from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    repository = Path(__file__).parents[1]
    shutil.copytree(repository / "config", tmp_path / "config")
    shutil.copytree(repository / "prompts", tmp_path / "prompts")
    for folder in ("input", "analyse", "consulting", "logs", "checkpoints"):
        (tmp_path / folder).mkdir()
    (tmp_path / "input" / "case.md").write_text(
        "# Work withdrawal\n\nAlex has spoken less in meetings since a team reorganization. "
        "Alex reported worrying that colleagues would judge every comment. The case gives no childhood, "
        "medical, relationship, or non-work context.",
        encoding="utf-8",
    )
    return tmp_path
