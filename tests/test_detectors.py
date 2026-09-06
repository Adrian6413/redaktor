from redaktor.detectors import find_findings

VALID_PESEL = "44051401359"
VALID_NIP = "1111111111"
VALID_NRB = "67101010000000000012345678"


def test_wykrywa_poprawny_pesel():
    findings = find_findings(f"Klient o numerze PESEL {VALID_PESEL} zamowil produkt.")
    assert [f.kind for f in findings] == ["PESEL"]
    assert findings[0].value == VALID_PESEL


def test_nie_wykrywa_11_cyfr_ze_zla_suma_kontrolna():
    # losowy 11-cyfrowy numer zamowienia, nie PESEL
    findings = find_findings("Numer zamowienia: 12345678901")
    assert findings == []


def test_wykrywa_email():
    findings = find_findings("Kontakt: jan.kowalski@firma.com.pl w sprawie umowy.")
    assert [f.kind for f in findings] == ["EMAIL"]
    assert findings[0].value == "jan.kowalski@firma.com.pl"


def test_wykrywa_telefon():
    findings = find_findings("Zadzwon pod 501 234 567 w razie pytan.")
    assert [f.kind for f in findings] == ["TELEFON"]


def test_wykrywa_nip_z_myslnikami():
    findings = find_findings("NIP firmy: 111-111-11-11 (przykladowy, poprawna suma).")
    assert [f.kind for f in findings] == ["NIP"]


def test_wykrywa_nrb_i_nie_myli_go_z_pesel_w_srodku():
    findings = find_findings(f"Prosze o przelew na konto {VALID_NRB}.")
    assert [f.kind for f in findings] == ["NRB"]
    assert findings[0].value == VALID_NRB


def test_kilka_roznych_danych_naraz():
    text = (
        f"PESEL: {VALID_PESEL}, email: test@example.com, "
        f"telefon: 601 111 222, konto: {VALID_NRB}"
    )
    findings = find_findings(text)
    kinds = sorted(f.kind for f in findings)
    assert kinds == ["EMAIL", "NRB", "PESEL", "TELEFON"]
