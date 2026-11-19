"""PrescriberRegistry, the simulated allow-list of prescriber codes.

A controlled medicine can only be dispensed when the prescription's prescriber
code is on this list. Ordinary medicines skip the check (R7, I9). is_allowed()
is a real membership test, so a non-empty string alone is not enough. Only
fictional codes such as PRB-001 are stored (N2).

Codes are trimmed and upper-cased on the way in and on lookup, so "prb-001",
" PRB-001 " and "PRB-001" all match. is_allowed() returns False for None, for
non-strings and for blank strings. The repository loads the codes from the
prescribers table at startup and the service calls is_allowed() inside
dispense. add() and remove() exist so tests can set up a known list.
"""

from __future__ import annotations

from collections.abc import Iterable

from pharmacy.domain.exceptions import PharmacyError

__all__ = ["PrescriberRegistry"]


class PrescriberRegistry:
    def __init__(self, allowed_codes: Iterable[str] | None = None) -> None:
        self._codes: set[str] = set()
        if allowed_codes is None:
            return
        if isinstance(allowed_codes, (str, bytes)):
            raise PharmacyError(
                f"Invalid allowed codes: {allowed_codes!r}. "
                "Pass a collection of codes, not a single string."
            )
        for code in allowed_codes:
            self.add(code)

    def is_allowed(self, code: str | None) -> bool:
        if not isinstance(code, str):
            return False
        normalised = code.strip().upper()
        return bool(normalised) and normalised in self._codes

    def add(self, code: str) -> None:
        self._codes.add(self._normalise(code, "add"))

    def remove(self, code: str) -> None:
        normalised = self._normalise(code, "remove")
        if normalised not in self._codes:
            raise PharmacyError(f"Prescriber {code!r} is not on the allow-list.")
        self._codes.remove(normalised)

    def codes(self) -> frozenset[str]:
        return frozenset(self._codes)

    def __contains__(self, code: object) -> bool:
        return self.is_allowed(code)  # type: ignore[arg-type]

    def __len__(self) -> int:
        return len(self._codes)

    def __repr__(self) -> str:
        return f"PrescriberRegistry({sorted(self._codes)!r})"

    def __str__(self) -> str:
        n = len(self._codes)
        return f"PrescriberRegistry({n} code{'s' if n != 1 else ''})"

    @staticmethod
    def _normalise(code: object, action: str) -> str:
        if not isinstance(code, str) or not code.strip():
            raise PharmacyError(
                f"Invalid prescriber code to {action}: {code!r}. "
                "Must be a non-empty string."
            )
        return code.strip().upper()