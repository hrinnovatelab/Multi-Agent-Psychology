from dataclasses import fields

from app.models import Revision


def test_revision_schema_contains_auditable_rationale_not_hidden_reasoning() -> None:
    names = {field.name for field in fields(Revision)}
    assert "concise_rationale" in names
    assert "counterargument_considered" in names
    assert "chain_of_thought" not in names
    assert "hidden_reasoning" not in names
