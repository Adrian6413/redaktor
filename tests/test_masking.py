from redaktor.masking import redact_text

VALID_PESEL = "44051401359"


def test_redact_text_podmienia_dane_na_etykiete():
    text = f"PESEL: {VALID_PESEL}."
    clean, entries = redact_text(text)
    assert VALID_PESEL not in clean
    assert "[USUNIĘTO-PESEL]" in clean
    assert len(entries) == 1
    assert entries[0].kind == "PESEL"


def test_redact_text_bez_danych_nie_zmienia_tekstu():
    text = "To jest zwykly tekst bez zadnych danych osobowych."
    clean, entries = redact_text(text)
    assert clean == text
    assert entries == []


def test_maskowany_podglad_nie_ujawnia_pelnej_wartosci():
    _, entries = redact_text(f"PESEL: {VALID_PESEL}.")
    preview = entries[0].masked_preview
    assert VALID_PESEL not in preview
    assert "*" in preview
    assert preview.startswith("44")
    assert preview.endswith("59")
