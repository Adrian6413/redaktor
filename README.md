# redaktor

[![CI](https://github.com/Adrian6413/redaktor/actions/workflows/ci.yml/badge.svg)](https://github.com/Adrian6413/redaktor/actions/workflows/ci.yml)

Anonimizator dokumentów - wczytuje PDF/DOCX, wykrywa PESEL, NIP, numer
konta bankowego, e-mail i telefon, zamazuje je i zwraca czysty plik
plus raport z tego, co znalazł.

```
$ redaktor umowa.docx
Znaleziono 3 danych osobowych:
  EMAIL: 1
  PESEL: 1
  TELEFON: 1

Szczegóły (wartości zamaskowane):
  PESEL: 44**e***59
  EMAIL: ja*******@f*****.pl
  TELEFON: 60*****22

Czysty plik zapisano jako: umowa_czysty.docx
Raport zapisano jako: umowa_czysty.docx.raport.json
```

## Problem

Każda firma, która wysyła dokumenty na zewnątrz (do audytora, do
publikacji, do innego działu bez dostępu do danych osobowych), musi
ręcznie przeglądać treść i zamazywać PESEL-e, numery kont, maile,
telefony. To żmudne i łatwo coś przeoczyć - a jeden przeoczony PESEL
w publicznie udostępnionym dokumencie to realny problem z RODO.

## Instalacja

Wymaga Pythona 3.11+.

```bash
git clone <adres-repo>
cd redaktor
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Użycie

```bash
redaktor umowa.docx
redaktor faktura.pdf
redaktor umowa.docx --output czysta_wersja.docx
```

Program zapisuje dwa pliki: czysty dokument (bez danych osobowych)
i raport JSON z listy tego, co znalazł (z zamaskowanym podglądem
każdej wartości - sam raport nie ujawnia pełnych danych).

## Jak to działa (w skrócie)

1. **Wykrywanie** (`detectors.py`) - wyrażenia regularne szukają
   kandydatów: 11 cyfr pod rząd (PESEL), 10 cyfr albo format z myślnikami
   (NIP), 26 cyfr (numer konta), adresy e-mail, ciągi 9 cyfr (telefon).
2. **Filtrowanie sumą kontrolną** (`checksums.py`) - PESEL, NIP i numer
   konta mają matematyczne sumy kontrolne. Bez tego kroku każdy losowy
   11-cyfrowy numer zamówienia zostałby uznany za PESEL - suma kontrolna
   odsiewa większość takich fałszywych trafień.
3. **Zamazywanie** (`masking.py`) - znalezione dane są podmieniane na
   etykiety typu `[USUNIĘTO-PESEL]`, a do raportu trafia tylko
   zamaskowany podgląd wartości, nie pełne dane.
4. **Zapis pliku** - dla `.docx` dane są usuwane wprost z akapitów
   i komórek tabel w oryginalnym pliku (format zachowany). Dla `.pdf`
   program wyciąga czysty tekst i zapisuje go jako `.txt` - powód opisany
   w "Ograniczeniach" poniżej.

## Ograniczenia

- **PDF wychodzi jako `.txt`, nie `.pdf`.** Wierne odtworzenie PDF-a
  z czarnymi prostokątami dokładnie na miejscu usuniętych danych
  wymagałoby precyzyjnego wyliczania współrzędnych tekstu na stronie -
  łatwo o błąd, który zostawiłby fragment danych czytelny. Zamiast
  ryzykować częściowo "prawie" zanonimizowany PDF, program świadomie
  wyciąga czysty tekst - gwarantuje to, że dane naprawdę znikają,
  kosztem utraty oryginalnego układu strony.
- **Suma kontrolna nie łapie wszystkiego.** Telefon nie ma sumy
  kontrolnej (bo żadna nie istnieje) - każdy ciąg 9 cyfr w odpowiednim
  formacie jest traktowany jak potencjalny numer telefonu, co czasem
  da fałszywy alarm (np. na numerze referencyjnym).
- **Skanowane obrazy w PDF nie zadziałają.** Program czyta tekst
  zapisany w pliku PDF - zeskanowana strona zapisana jako obrazek
  wymagałaby OCR-u, którego tu nie ma.
- **Fałszywie poprawna suma kontrolna wciąż może się zdarzyć.** Suma
  kontrolna odsiewa większość przypadkowych ciągów cyfr, ale
  matematycznie nie da 100% pewności - losowy numer z poprawną sumą
  zdarza się rzadko, ale nie jest niemożliwy.

## Rozwój

```bash
pip install -e . pytest ruff
pytest        # testy
ruff check .  # lint
```
