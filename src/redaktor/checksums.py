"""Sumy kontrolne PESEL/NIP/NRB - odsiewają przypadkowe ciągi cyfr.

Bez tego każdy 11-cyfrowy numer w tekście zostałby uznany za PESEL,
a większość takich "trafień" to zwykłe numery zamówień czy faktur.
Suma kontrolna nie daje 100% pewności (fałszywy numer może przypadkiem
mieć poprawną sumę), ale odrzuca zdecydowaną większość przypadkowych
ciągów cyfr.
"""

_PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
_NIP_WEIGHTS = (6, 5, 7, 2, 3, 4, 5, 6, 7)


def is_valid_pesel(digits: str) -> bool:
    """digits: dokładnie 11 cyfr (bez separatorów)."""
    if len(digits) != 11 or not digits.isdigit():
        return False

    checksum = sum(int(d) * w for d, w in zip(digits[:10], _PESEL_WEIGHTS, strict=True))
    control = (10 - checksum % 10) % 10
    return control == int(digits[10])


def is_valid_nip(digits: str) -> bool:
    """digits: dokładnie 10 cyfr (bez separatorów)."""
    if len(digits) != 10 or not digits.isdigit():
        return False

    checksum = sum(int(d) * w for d, w in zip(digits[:9], _NIP_WEIGHTS, strict=True))
    control = checksum % 11
    if control == 10:
        return False  # taki numer nie ma poprawnej cyfry kontrolnej - z definicji błędny
    return control == int(digits[9])


def iban_mod97_valid(iban: str) -> bool:
    """Standardowy test mod-97 z normy IBAN (ISO 13616).

    Pierwsze 4 znaki (kod kraju + 2 cyfry kontrolne) przenosimy na koniec,
    litery zamieniamy na cyfry (A=10 ... Z=35, stąd `int(znak, 36)`),
    i sprawdzamy, czy tak powstała liczba mod 97 daje resztę 1.
    """
    iban = iban.replace(" ", "").upper()
    rearranged = iban[4:] + iban[:4]
    numeric = "".join(str(int(ch, 36)) for ch in rearranged)
    return int(numeric) % 97 == 1


def is_valid_nrb(digits: str) -> bool:
    """digits: dokładnie 26 cyfr polskiego numeru rachunku (bez "PL" i spacji).

    Polski NRB ma tę własność, że doklejenie "PL" z przodu daje poprawny
    numer IBAN - więc walidacja to zwykły test mod-97 z normy IBAN.
    """
    if len(digits) != 26 or not digits.isdigit():
        return False
    return iban_mod97_valid("PL" + digits)
