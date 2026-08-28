from __future__ import annotations

from datetime import datetime

from app.utils.slug import safe_slug


def artifact_stem(case_name: str, timestamp: datetime) -> str:
    return f"criticize-log-{timestamp.strftime('%Y-%m-%d-%H-%M-%S')}-{safe_slug(case_name)}"
