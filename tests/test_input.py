from pathlib import Path

import pytest

from app.input import CaseInputError, load_case


def test_markdown_input_loads(project_root: Path) -> None:
    case = load_case("case.md", project_root / "input")
    assert case.title == "Work withdrawal"
    assert "reorganization" in case.content


def test_path_escape_is_rejected(project_root: Path) -> None:
    with pytest.raises(CaseInputError, match="directly inside"):
        load_case("../outside.md", project_root / "input")
