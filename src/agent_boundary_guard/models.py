from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str
    line: int
    snippet: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
