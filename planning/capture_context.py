"""Save the installed AIDRIN guidance used for this experiment."""

import hashlib
import importlib.metadata
import json
import subprocess
import sysconfig
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    command = Path(sysconfig.get_path("scripts")) / "aidrin.exe"
    if not command.exists():
        command = Path(sysconfig.get_path("scripts")) / "aidrin"
    result = subprocess.run(
        [str(command), "list"], capture_output=True, text=True, check=True, timeout=60
    )
    catalogue = json.loads(result.stdout)
    if not isinstance(catalogue, dict) or not catalogue:
        raise ValueError("AIDRIN did not return a catalogue")
    package = importlib.metadata.distribution("aidrin")
    skill = Path(package.locate_file("aidrin/skill/SKILL.md"))
    reference = Path(package.locate_file("aidrin/skill/reference/metrics.md"))
    snapshot = {
        "aidrin_version": package.version,
        "catalogue_source": "aidrin list",
        "skill_source": "aidrin/skill/SKILL.md in the installed distribution",
        "hash_normalization": "CRLF line endings are converted to LF before hashing",
        "skill_sha256": hashlib.sha256(skill.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "metrics_reference_sha256": hashlib.sha256(reference.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "metrics": catalogue,
    }
    (root / "catalogue.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Captured {sum(map(len, catalogue.values()))} metrics from AIDRIN {package.version}")


if __name__ == "__main__":
    main()
