from pathlib import Path

from portal.config import UPLOAD_ROOT


def save(filename, content):
    target = Path(UPLOAD_ROOT) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as fh:
        fh.write(content)
    return str(target)
