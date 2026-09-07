"""Wiersz poleceń: `redaktor plik.docx` albo `redaktor plik.pdf`."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from redaktor.docx_processor import process_docx
from redaktor.masking import ReportEntry
from redaktor.pdf_processor import process_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="redaktor",
        description="Anonimizuje dane osobowe (PESEL, NIP, konto, e-mail, telefon) w PDF/DOCX.",
    )
    parser.add_argument("plik", type=Path, help="Dokument .pdf albo .docx do zanonimizowania")
    parser.add_argument(
        "--output",
        type=Path,
        help="Ścieżka pliku wynikowego (domyślnie: <nazwa>_czysty z odpowiednim rozszerzeniem)",
    )
    return parser


def _default_output_path(input_path: Path) -> Path:
    suffix = ".txt" if input_path.suffix.lower() == ".pdf" else input_path.suffix
    return input_path.with_name(f"{input_path.stem}_czysty{suffix}")


def _print_report(entries: list[ReportEntry]) -> None:
    if not entries:
        print("Nie znaleziono żadnych danych osobowych.")
        return

    counts = Counter(entry.kind for entry in entries)
    print(f"Znaleziono {len(entries)} danych osobowych:")
    for kind, count in sorted(counts.items()):
        print(f"  {kind}: {count}")

    print("\nSzczegóły (wartości zamaskowane):")
    for entry in entries:
        print(f"  {entry.kind}: {entry.masked_preview}")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.plik.is_file():
        print(f"Błąd: {args.plik} nie jest plikiem", file=sys.stderr)
        return 1

    suffix = args.plik.suffix.lower()
    output_path = args.output or _default_output_path(args.plik)

    if suffix == ".docx":
        entries = process_docx(args.plik, output_path)
    elif suffix == ".pdf":
        entries = process_pdf(args.plik, output_path)
    else:
        print(f"Błąd: nieobsługiwany format {suffix} (obsługiwane: .pdf, .docx)", file=sys.stderr)
        return 1

    _print_report(entries)
    print(f"\nCzysty plik zapisano jako: {output_path}")

    report_path = output_path.with_suffix(output_path.suffix + ".raport.json")
    report_data = [{"typ": e.kind, "podglad": e.masked_preview} for e in entries]
    report_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Raport zapisano jako: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
