"""Stable input identities and software revision metadata for experiment reports."""

from __future__ import annotations

import json
import subprocess
from hashlib import sha256
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_identity(path: Path) -> dict[str, str | int]:
    resolved = path.resolve()
    return {
        "filename": path.name,
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def dataset_fingerprint(inputs: dict[str, dict], configuration: dict) -> str:
    payload = json.dumps(
        {"inputs": inputs, "configuration": configuration},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def git_revision(repository_root: Path) -> dict[str, str | bool | None]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repository_root,
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        return {"commit": commit, "dirty": bool(status.strip())}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
