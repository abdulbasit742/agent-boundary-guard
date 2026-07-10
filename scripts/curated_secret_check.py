from __future__ import annotations

from pathlib import Path
import sys

TARGETS = [
    Path("README.md"),
    Path("SECURITY.md"),
    Path("ARCHITECTURE.md"),
    Path("CONTRIBUTING.md"),
    Path("docs"),
    Path("src"),
    Path("tests"),
    Path(".github"),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for target in TARGETS:
        candidates = [target] if target.is_file() else list(target.rglob("*"))
        for path in candidates:
            if not path.is_file():
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pyc"}:
                continue
            files.append(path)
    return files


def main() -> int:
    blocked: list[str] = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "BEGIN PRIVATE KEY" in text:
            blocked.append(str(path))
        if path.name.startswith(".env") and path.name != ".env.example":
            blocked.append(str(path))
    if blocked:
        print("Blocked files detected:")
        print("\n".join(blocked))
        return 1
    print("Curated secret check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
