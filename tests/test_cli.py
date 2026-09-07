import json

from docx import Document

from redaktor.cli import main

VALID_PESEL = "44051401359"


def test_main_bledny_plik_zwraca_blad(tmp_path, capsys):
    exit_code = main([str(tmp_path / "nie_istnieje.docx")])
    assert exit_code == 1
    assert "nie jest plikiem" in capsys.readouterr().err


def test_main_nieobslugiwany_format(tmp_path, capsys):
    plik = tmp_path / "dane.txt"
    plik.write_text("cos", encoding="utf-8")

    exit_code = main([str(plik)])

    assert exit_code == 1
    assert "nieobsługiwany format" in capsys.readouterr().err


def test_main_docx_tworzy_czysty_plik_i_raport(tmp_path, capsys):
    input_path = tmp_path / "umowa.docx"
    doc = Document()
    doc.add_paragraph(f"PESEL klienta: {VALID_PESEL}")
    doc.save(str(input_path))

    exit_code = main([str(input_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "PESEL: 1" in out

    output_path = tmp_path / "umowa_czysty.docx"
    assert output_path.exists()

    report_path = tmp_path / "umowa_czysty.docx.raport.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report[0]["typ"] == "PESEL"
    assert VALID_PESEL not in json.dumps(report)
