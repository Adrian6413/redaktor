"""Szukanie danych osobowych w tekście: PESEL, NIP, numer konta, e-mail, telefon."""

import re
from dataclasses import dataclass

from redaktor.checksums import is_valid_nip, is_valid_nrb, is_valid_pesel


@dataclass(frozen=True, slots=True)
class Finding:
    kind: str  # "PESEL" / "NIP" / "NRB" / "EMAIL" / "TELEFON"
    value: str  # dokładnie to, co znaleziono w tekście (z separatorami)
    start: int
    end: int


_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_NRB_RE = re.compile(r"\b(?:PL)?\d{2}(?:[ -]?\d{4}){6}\b|\b(?:PL)?\d{26}\b")
_PESEL_RE = re.compile(r"\b\d{11}\b")
_NIP_RE = re.compile(r"\b\d{3}-\d{2}-\d{2}-\d{3}\b|\b\d{3}-\d{3}-\d{2}-\d{2}\b|\b\d{10}\b")
# (?<!\d) / (?!\d) zamiast \b na obu koncach - \b samo w sobie nie
# przeszkodzilo dopasowaniu sie do fragmentu dluzszego ciagu cyfr (np.
# 13-cyfrowego numeru zamowienia), bo w srodku ciagu samych cyfr nie ma
# zadnej granicy \b, do ktorej mozna by sie odwolac
_PHONE_RE = re.compile(r"(?<!\d)(?:\+48|0048)?[ -]?(?:\d{3}[ -]?){2}\d{3}(?!\d)")

_ONLY_DIGITS = re.compile(r"\D")


def _digits_only(text: str) -> str:
    return _ONLY_DIGITS.sub("", text)


def _find_non_overlapping(pattern: re.Pattern, text: str, taken: list[tuple[int, int]]) -> list:
    matches = []
    for m in pattern.finditer(text):
        if any(m.start() < end and start < m.end() for start, end in taken):
            continue
        matches.append(m)
    return matches


def find_findings(text: str) -> list[Finding]:
    """Szuka wszystkich danych osobowych w tekście, od najdłuższych wzorców.

    Kolejność ma znaczenie: numer konta (26 cyfr) zawiera w sobie ciągi,
    które osobno wyglądałyby jak PESEL czy NIP, więc dłuższe/bardziej
    specyficzne wzorce sprawdzamy jako pierwsze i "rezerwujemy" ich zasięg,
    żeby krótsze wzorce nie próbowały dopasować się do ich fragmentu.
    """
    taken: list[tuple[int, int]] = []
    findings: list[Finding] = []

    for kind, pattern, validate in (
        ("NRB", _NRB_RE, is_valid_nrb),
        ("PESEL", _PESEL_RE, is_valid_pesel),
        ("NIP", _NIP_RE, is_valid_nip),
    ):
        for m in _find_non_overlapping(pattern, text, taken):
            digits = _digits_only(m.group())
            # rezerwujemy zasięg nawet przy złej sumie kontrolnej - inaczej
            # słabszy wzorzec (telefon) próbowałby dopasować się do jego
            # fragmentu, tak jak przy 11-cyfrowym numerze zamówienia
            taken.append((m.start(), m.end()))
            if not validate(digits):
                continue
            findings.append(Finding(kind=kind, value=m.group(), start=m.start(), end=m.end()))

    for m in _find_non_overlapping(_EMAIL_RE, text, taken):
        findings.append(Finding(kind="EMAIL", value=m.group(), start=m.start(), end=m.end()))
        taken.append((m.start(), m.end()))

    for m in _find_non_overlapping(_PHONE_RE, text, taken):
        digits = _digits_only(m.group()).removeprefix("48").removeprefix("0048")
        if len(digits) != 9:
            continue
        findings.append(Finding(kind="TELEFON", value=m.group(), start=m.start(), end=m.end()))
        taken.append((m.start(), m.end()))

    return sorted(findings, key=lambda f: f.start)
