import re
from datetime import datetime

from app.outputs.filenames import artifact_stem


def test_safe_timestamped_filename() -> None:
    value = artifact_stem("A Case / with unsafe chars", datetime(2026, 8, 28, 17, 30, 5))
    assert re.fullmatch(r"criticize-log-2026-08-28-17-30-05-a-case-with-unsafe-chars", value)
