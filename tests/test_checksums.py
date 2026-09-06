from redaktor.checksums import is_valid_nip, is_valid_nrb, is_valid_pesel


def test_poprawny_pesel():
    assert is_valid_pesel("44051401359") is True


def test_pesel_ze_zla_cyfra_kontrolna():
    assert is_valid_pesel("44051401350") is False


def test_pesel_zla_dlugosc():
    assert is_valid_pesel("123") is False


def test_poprawny_nip():
    assert is_valid_nip("1111111111") is True


def test_nip_ze_zla_cyfra_kontrolna():
    assert is_valid_nip("1111111112") is False


def test_nip_zla_dlugosc():
    assert is_valid_nip("123") is False


def test_poprawny_nrb():
    assert is_valid_nrb("67101010000000000012345678") is True


def test_nrb_z_bledna_suma_kontrolna():
    zly = "66101010000000000012345678"
    assert is_valid_nrb(zly) is False


def test_nrb_zla_dlugosc():
    assert is_valid_nrb("123") is False
