from redaktor.pdf_processor import redact_pdf_pages

VALID_PESEL = "44051401359"


def test_redact_pdf_pages_zamazuje_na_kazdej_stronie():
    pages = [
        f"Strona 1. Klient PESEL {VALID_PESEL}.",
        "Strona 2. Tu nie ma zadnych danych.",
    ]

    clean_text, entries = redact_pdf_pages(pages)

    assert VALID_PESEL not in clean_text
    assert "[USUNIĘTO-PESEL]" in clean_text
    assert "Strona 2" in clean_text
    assert len(entries) == 1


def test_redact_pdf_pages_pusta_lista():
    clean_text, entries = redact_pdf_pages([])
    assert clean_text == ""
    assert entries == []
