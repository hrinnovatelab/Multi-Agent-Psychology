from __future__ import annotations

import re


DIAGNOSIS_CERTAINTY = re.compile(
    r"\b(?:this person|the person|they|he|she)\s+(?:has|suffers from)\s+[A-Z][A-Za-z -]*(?:Disorder|Syndrome)\b",
    re.I,
)
MEDICATION_ADVICE = re.compile(r"\b(?:prescribe|take|start|stop)\s+(?:medication|antidepressants?|antipsychotics?)\b", re.I)


def sanitize_educational_text(text: str) -> tuple[str, list[str]]:
    flags: list[str] = []
    if DIAGNOSIS_CERTAINTY.search(text):
        flags.append("diagnostic certainty")
        text = DIAGNOSIS_CERTAINTY.sub(
            "The description may overlap with a clinical phenomenon, but the available information is insufficient for diagnosis",
            text,
        )
    if MEDICATION_ADVICE.search(text):
        flags.append("medication advice")
        text = MEDICATION_ADVICE.sub("seek guidance from a qualified prescribing professional about medication", text)
    return text, flags


def educational_safety_note(risk_flags: list[str]) -> str:
    base = (
        "This material is for education only. It is not diagnosis, therapy, crisis support, "
        "or a substitute for assessment by a qualified professional."
    )
    if risk_flags:
        base += (
            " The case contains a possible immediate safety concern. A qualified human or local "
            "emergency/crisis resource should be contacted; this academic debate is not an adequate response."
        )
    return base
