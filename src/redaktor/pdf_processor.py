"""Anonimizacja plików .pdf.

pypdf potrafi wyciągnąć tekst ze stron, ale nie potrafi (bez sporego
dodatkowego kodu do rysowania i pozycjonowania) wiernie odtworzyć
oryginalny układ strony z zamazanymi fragmentami w dokładnie tych samych
miejscach. Zamiast robić to "na pół gwizdka" (co przy błędzie w
pozycjonowaniu mogłoby zostawić widoczne dane - fatalne dla narzędzia od
RODO), wyciągamy czysty tekst i zapisujemy go jako .txt. Patrz sekcja
"Ograniczenia" w README.

`redact_pdf_pages` działa na już wyciągniętym tekście (liście stron jako
stringi), więc dającą się przetestować bez plikow PDF na dysku - patrz
tests/test_pdf_processor.py. `process_pdf` to już tylko cienka warstwa,
która woła pypdf i zapisuje wynik.
"""

from pathlib import Path

from pypdf import PdfReader

from redaktor.masking import ReportEntry, redact_text


def redact_pdf_pages(pages_text: list[str]) -> tuple[str, list[ReportEntry]]:
    """Zamazuje dane na każdej stronie osobno i skleja wynik w jeden tekst."""
    all_entries: list[ReportEntry] = []
    clean_pages = []

    for page_text in pages_text:
        clean, entries = redact_text(page_text)
        clean_pages.append(clean)
        all_entries.extend(entries)

    separator = "\n\n--- koniec strony ---\n\n"
    return separator.join(clean_pages), all_entries


def process_pdf(input_path: str | Path, output_path: str | Path) -> list[ReportEntry]:
    """Wczytuje .pdf, zamazuje dane osobowe i zapisuje wynik jako plik .txt."""
    reader = PdfReader(str(input_path))
    pages_text = [page.extract_text() or "" for page in reader.pages]

    clean_text, entries = redact_pdf_pages(pages_text)
    Path(output_path).write_text(clean_text, encoding="utf-8")

    return entries
