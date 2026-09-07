"""Anonimizacja plików .docx - podmienia dane wprost w akapitach dokumentu."""

from pathlib import Path

from docx import Document

from redaktor.masking import ReportEntry, redact_text


def _replace_paragraph_text(paragraph, clean: str) -> None:
    # jeden run z czystym tekstem zamiast oryginalnych - traci się
    # ewentualne różnice w formatowaniu w środku akapitu, ale gwarantuje,
    # że dane faktycznie znikają z pliku XML, a nie tylko "wizualnie"
    if paragraph.runs:
        paragraph.runs[0].text = clean
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(clean)


def process_docx(input_path: str | Path, output_path: str | Path) -> list[ReportEntry]:
    """Wczytuje .docx, zamazuje dane osobowe i zapisuje czysty plik obok."""
    document = Document(str(input_path))
    all_entries: list[ReportEntry] = []

    for paragraph in document.paragraphs:
        clean, entries = redact_text(paragraph.text)
        if not entries:
            continue
        all_entries.extend(entries)
        _replace_paragraph_text(paragraph, clean)

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    clean, entries = redact_text(paragraph.text)
                    if not entries:
                        continue
                    all_entries.extend(entries)
                    _replace_paragraph_text(paragraph, clean)

    document.save(str(output_path))
    return all_entries
