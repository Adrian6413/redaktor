"""Zamazywanie znalezionych danych w tekście i przygotowanie wpisów do raportu."""

from dataclasses import dataclass

from redaktor.detectors import Finding, find_findings

_LABELS = {
    "PESEL": "[USUNIĘTO-PESEL]",
    "NIP": "[USUNIĘTO-NIP]",
    "NRB": "[USUNIĘTO-NR-KONTA]",
    "EMAIL": "[USUNIĘTO-EMAIL]",
    "TELEFON": "[USUNIĘTO-TELEFON]",
}


@dataclass(frozen=True, slots=True)
class ReportEntry:
    kind: str
    masked_preview: str  # np. "8501******9" - nigdy pełna wartość


def _mask_preview(value: str) -> str:
    """Zostawia pierwsze i ostatnie 2 znaki, resztę zamienia na gwiazdki.

    Raport ma pomóc zweryfikować, co program znalazł, ale sam raport
    nie powinien stać się nowym źródłem wycieku danych.
    """
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def redact_text(text: str) -> tuple[str, list[ReportEntry]]:
    """Zwraca (tekst z zamazanymi danymi, lista wpisów do raportu)."""
    findings: list[Finding] = find_findings(text)

    result = []
    last_end = 0
    entries = []
    for finding in findings:
        result.append(text[last_end : finding.start])
        result.append(_LABELS[finding.kind])
        entries.append(ReportEntry(kind=finding.kind, masked_preview=_mask_preview(finding.value)))
        last_end = finding.end
    result.append(text[last_end:])

    return "".join(result), entries
