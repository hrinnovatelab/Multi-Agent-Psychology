from pathlib import Path

import pytest

from app.agents.validator import EpistemicValidatorAgent
from app.models import Claim, Confidence, EpistemicType
from app.providers.mock import MockProvider
from app.safety import sanitize_educational_text
from app.utils.prompts import PromptRepository
from tests.helpers import run_mock


@pytest.mark.asyncio
async def test_unsupported_diagnosis_is_downgraded(project_root: Path) -> None:
    claim = Claim("CLM-001", "beck", 0, "The person has Major Depressive Disorder.", EpistemicType.INTERPRETATION, [], confidence=Confidence.HIGH)
    result = await EpistemicValidatorAgent(MockProvider(), 0).validate(claim, PromptRepository(project_root / "prompts"))
    assert result.epistemic_type is EpistemicType.HYPOTHESIS
    assert result.confidence is Confidence.LOW
    assert result.overreach_risk == "high"


def test_code_level_safety_removes_diagnostic_certainty() -> None:
    text, flags = sanitize_educational_text("The person has Major Depressive Disorder.")
    assert "has Major Depressive Disorder" not in text
    assert flags == ["diagnostic certainty"]


@pytest.mark.asyncio
async def test_missing_case_information_remains_explicit(project_root: Path) -> None:
    (project_root / "input" / "case.md").write_text("# Short case\n\nSam stopped attending one meeting.")
    result = await run_mock(project_root)
    assert "more detailed case information" in result.state.intake.missing_information
    serialized = str(result.state.to_dict()).lower()
    assert "childhood trauma" not in serialized


@pytest.mark.asyncio
async def test_final_output_contains_no_diagnosis_heading(project_root: Path) -> None:
    result = await run_mock(project_root)
    assert "## Diagnosis" not in result.outputs.analyse.read_text(encoding="utf-8")
    assert "## Treatment Plan" not in result.outputs.consulting.read_text(encoding="utf-8")
