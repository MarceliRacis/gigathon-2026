# 🔴 ARES-MISSION — Symulator Marsjańskiego Łazika

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/Licencja-MIT-green?style=for-the-badge)](LICENSE)
[![Gigathon](https://img.shields.io/badge/Gigathon-2026-orange?style=for-the-badge&logo=rocket&logoColor=white)](https://git.racis.dev/marceliracis/gigathon-2026)
[![Stdlib Only](https://img.shields.io/badge/Zale%C5%BCno%C5%9Bci-brak%20(tylko%20stdlib)-success?style=for-the-badge&logo=checkmarx)](https://docs.python.org/3.11/library/index.html)
[![Terminal](https://img.shields.io/badge/UI-Terminal%20%2F%20CLI-black?style=for-the-badge&logo=gnometerminal&logoColor=white)]()

[![Gitea](https://img.shields.io/badge/Gitea-Oryginalne%20Repo-609926?style=for-the-badge&logo=gitea&logoColor=white)](https://git.racis.dev/marceliracis/gigathon-2026)
[![GitHub Mirror](https://img.shields.io/badge/GitHub-Mirror-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MarceliRacis/gigathon-2026)

> **Symulator misji łazika na dwuwymiarowej powierzchni Marsa.**  
> Steruj łazikiem, zbieraj sygnały telemetryczne, przeżyj zdarzenia losowe i wróć zanim skończy się energia.  
> Napisany w czystym Pythonie 3.11 — bez żadnych zewnętrznych bibliotek.

</div>

---

## 📋 Spis treści

- [Demo](#-demo)
- [Funkcje](#-funkcje)
- [Architektura](#-architektura-projektu)
- [Opis plików](#-opis-plików)
- [Instalacja i uruchomienie](#-instalacja-i-uruchomienie)
- [Rozgrywka](#-rozgrywka)
- [Świat i pola](#-świat-i-pola)
- [Zdarzenia losowe](#-zdarzenia-losowe)
- [System punktacji](#-system-punktacji)
- [Warunki zakończenia](#-warunki-zakończenia)
- [Biblioteka `lib.py`](#-biblioteka-libpy)
- [Konfiguracja](#-konfiguracja-configpy)
- [Wymagania](#-wymagania)

---

## 🎬 Demo

```
═══════════════════════════════════════════════════════════════════════════════
                           ARES-MISSION  SYMULATOR
═══════════════════════════════════════════════════════════════════════════════

  ▸ KONFIGURACJA MISJI  ────────────────────────────────────────────────────
  ℹ Podaj parametry nowej wyprawy. Wciśnij ENTER aby użyć wartości domyślnej.

  ▶ Nazwa łazika (domyślnie: ARES-1): Perseverance
  ✔ Nazwa: Perseverance

  ▶ Pozycja startowa X [−50–50, domyślnie 0]: 0
  ▶ Pozycja startowa Y [−50–50, domyślnie 0]: 0
  ✔ Pozycja startowa: (+0, +0)

──────────────────────────── [ KROK 1 / 30 ] ──────────────────────────────
  Pozycja: (+0, +0)   Energia: [████████████████░░░░]  80/100

  ▶ Kierunek [n/s/e/w/ne/nw/se/sw]: ne
  → Wybrano: Północny-Wschód
  ✔ Ruch: (+0, +0) → (+1, +1)  (koszt: 3 energii)

  · Teren normalny — brak specjalnych efektów.

  ·············································
  ★ ZDARZENIE LOSOWE: ROZBŁYSK SŁONECZNY
  → Intensywne promieniowanie słoneczne ładuje panele!
  → Skutek: +12 energii
  ·············································
```

---

## ✨ Funkcje

| Funkcja | Opis |
|---|---|
| 🎮 **Sterowanie** | 8 kierunków ruchu (N/S/E/W + diagonale) |
| 🗺️ **Świat 2D** | Mapa 101×101 pól (`−50` do `+50`) z losowym generowaniem |
| ⚡ **Energia** | Pasek energii, koszt ruchu, bonusy i kary |
| 🌍 **5 typów pól** | Równina, burza pyłowa, lód, krater, sygnał, skała |
| 🎲 **7 zdarzeń losowych** | Rozbłysk, burza, osunięcie, antena, bateria, błąd systemu, wstrząs |
| 🏆 **3 wyniki** | Sukces / Częściowy sukces / Porażka |
| 📊 **System punktacji** | Zależny od trudności, energii, kroków i sygnałów |
| 🌈 **Kolory ANSI** | Pełne wsparcie 24-bit RGB w terminalu (własna biblioteka) |
| 🔁 **Replay** | Możliwość ponownego uruchomienia z nowymi parametrami |
| 🏅 **Tabela wyników** | Ranking z sesji z medalami |
| 🌱 **Seed** | Powtarzalne światy dzięki konfigurowalności generatora |

---

## 🏗️ Architektura projektu

```
gigathon-2026/
├── main.py          ← Punkt wejścia — orchestracja całego programu
├── lib.py           ← Własna biblioteka terminalna (kolory, ramki, animacje)
├── config.py        ← Stałe, konfiguracja trudności, typy pól
├── rover.py         ← Klasa łazika (stan, ruch, energia, historia)
├── world.py         ← Generator i mapa świata 2D
├── events.py        ← Silnik zdarzeń losowych
├── display.py       ← Wszystkie funkcje wyświetlania / UI w terminalu
├── setup.py         ← Zbieranie parametrów od użytkownika (onboarding)
├── simulation.py    ← Główna pętla symulacji, warunki końcowe, scoring
└── README.md        ← Ten plik
```

### Diagram zależności między modułami

```
main.py
├── display.py   ─────────────┐
├── setup.py     → rover.py   │
│                → world.py   ├── lib.py
│                → events.py  │
└── simulation.py             │
    ├── rover.py  ────────────┤
    ├── world.py  ────────────┤
    ├── events.py ────────────┤
    └── display.py ───────────┘
         │
         └── config.py  (importowany przez wszystkie moduły)
```

---

## 📁 Opis plików

### `main.py` — Punkt wejścia
Orkiestrator całego programu. Wywołuje ekran powitalny, zbiera parametry, uruchamia symulację i obsługuje pętlę `play_again`. Wyświetla tabelę wyników sesji przy wielu rozgrywkach.

### `lib.py` — Biblioteka terminalna ⭐
Własna biblioteka do obsługi terminala — **napisana od zera, bez zewnętrznych zależności**:
- Kody ANSI (16 kolorów + True Color 24-bit RGB)
- Funkcje stylizacji: `bold()`, `red()`, `green()`, `rgb(r, g, b, text)` itd.
- Rysowanie ramek z Unicode (`box()`, `separator()`, `header()`, `section()`)
- Pasek postępu (`progress_bar()`)
- Animacje: `typewrite()`, `spinner()`, `loading_bar()`, `blink_message()`
- Walidujące funkcje input: `prompt_int()`, `prompt_float()`, `prompt_choice()`
- Automatyczne wykrywanie obsługi kolorów (Windows, Unix, NO_COLOR, FORCE_COLOR)
- Obliczanie widocznej długości stringów (bez kodów ANSI) do wyrównywania

### `config.py` — Konfiguracja
Centralne miejsce na wszystkie stałe:
- Granice świata (`WORLD_MIN`, `WORLD_MAX`)
- Ustawienia poziomów trudności (easy/normal/hard)
- Typy pól i ich symbole
- Definicje 7 zdarzeń losowych
- Wartości punktacji

### `rover.py` — Łazik
Klasa `Rover` z pełnym stanem:
- Pozycja `(x, y)`, energia, krok, historia
- Ruch w 8 kierunkach z walidacją granic i kosztem energii
- Wymuszony ruch (zdarzenia) — `force_move()`
- Cofnięcie — `push_back()`
- Statystyki: `total_distance`, `signals_found`, `events_survived`, `craters_avoided`

### `world.py` — Świat 2D
Klasa `World`:
- Proceduralny generator mapy z seedem
- Słownik `{(x,y): typ_pola}` — efektywny i lekki
- Wykrywanie pola pod łazikiem i aplikacja efektów
- Lokalizacja celu z minimalną odległością od startu
- Ujawnianie celu przez zdarzenie anteny
- Podpowiedź kierunku do celu (`hint_direction()`)

### `events.py` — Zdarzenia losowe
Klasa `EventEngine`:
- Losowanie zdarzenia z prawdopodobieństwem zależnym od trudności
- 7 typów zdarzeń z różnymi efektami (`energy`, `pushback`, `reveal_goal`, `random_move`)
- Losowa wariacja ±20% wartości energetycznej
- Pełny log zdarzeń do raportu końcowego

### `display.py` — Wyświetlanie
Wszystkie funkcje UI terminala:
- Ekran powitalny z ASCII Art logo
- Briefing misji, legenda świata, parametry startowe
- Nagłówek kroku, menu kierunków, wyniki ruchu
- Efekty pola, zdarzenia losowe
- Ekran końca gry, szczegółowy raport końcowy

### `setup.py` — Konfiguracja wstępna
Interaktywne zbieranie parametrów misji z pełną walidacją:
- Nazwa łazika, pozycja startowa (X, Y), energia, trudność, limit kroków, seed

### `simulation.py` — Silnik symulacji
Główna pętla `while running`:
- Pobieranie ruchu od użytkownika
- Blokada skał przed ruchem
- Aplikacja efektów pola
- Losowanie i stosowanie zdarzeń
- Sprawdzanie 3 warunków zakończenia
- Obliczanie wyniku końcowego
- Budowanie raportu

---

## 🚀 Instalacja i uruchomienie

### Wymagania systemowe

- **Python 3.11** lub nowszy
- System operacyjny: Linux, macOS, Windows 10+
- Terminal z obsługą ANSI (domyślny terminal na Linux/macOS; Windows Terminal na Windows)
- **Brak** zewnętrznych bibliotek — tylko standardowa biblioteka Pythona

### Pobieranie

```bash
# Oryginalne repozytorium (Gitea)
git clone https://git.racis.dev/marceliracis/gigathon-2026.git

# Mirror (GitHub)
git clone https://github.com/MarceliRacis/gigathon-2026.git
```

### Uruchomienie

```bash
cd gigathon-2026
python main.py
```

lub (jeśli masz wiele wersji Pythona):

```bash
python3.11 main.py
```

### Windows

```powershell
cd gigathon-2026
python main.py
```

> ⚠️ Na Windows zalecane jest użycie **Windows Terminal** (nie klasycznego `cmd.exe`) dla pełnej obsługi kolorów ANSI.

---

## 🎮 Rozgrywka

### Parametry startowe

| Parametr | Zakres | Domyślnie | Opis |
|---|---|---|---|
| Nazwa łazika | tekst, max 24 znaki | `ARES-1` | Identyfikator misji |
| Pozycja X | `−50` do `+50` | `0` | Współrzędna startowa |
| Pozycja Y | `−50` do `+50` | `0` | Współrzędna startowa |
| Energia | `10` do `100` | `100` | Zasób energii łazika |
| Trudność | `easy/normal/hard` | `normal` | Poziom wyzwania |
| Maks. kroków | `5` do `100` | `30` | Limit czasu misji |
| Seed | liczba całkowita | losowy | Powtarzalne światy |

### Sterowanie

Wpisz kierunek i zatwierdź Enterem:

```
  NW   N   NE
   W   ●   E
  SW   S   SE
```

| Komenda | Kierunek |
|---|---|
| `n` | Północ (+Y) |
| `s` | Południe (−Y) |
| `e` | Wschód (+X) |
| `w` | Zachód (−X) |
| `ne` | Północny-Wschód |
| `nw` | Północny-Zachód |
| `se` | Południowy-Wschód |
| `sw` | Południowy-Zachód |
| `q` | Przerwij misję |

### Krok symulacji

Każdy krok wyświetla:
1. Numer kroku i postęp
2. Aktualną pozycję i energię (pasek)
3. Menu kierunków z dystansem do celu
4. Wynik ruchu (nowa pozycja, koszt energii)
5. Efekt pola (jeśli pole specjalne)
6. Zdarzenie losowe (jeśli wystąpiło)

---

## 🗺️ Świat i pola

Świat to kwadratowa mapa od `(−50, −50)` do `(+50, +50)`.

| Symbol | Typ pola | Efekt |
|---|---|---|
| `·` | **Równina** | Brak efektu |
| 💨 | **Burza pyłowa** | −8/12/18 energii (zależnie od trudności) |
| ❄ | **Pokład lodu** | +7/10/15 energii |
| 🕳 | **Krater** | Cofnięcie do poprzedniej pozycji |
| 📡 | **Sygnał** | +10/15/20 energii + postęp misji |
| 🪨 | **Skała** | Ruch zablokowany |

> Ilość pól każdego typu zależy od poziomu trudności.

---

## 🎲 Zdarzenia losowe

Program zawiera **7 różnych zdarzeń losowych** (wymagane minimum: 2):

| Symbol | Zdarzenie | Efekt |
|---|---|---|
| ☀ | **Rozbłysk słoneczny** | +12 energii (±20%) |
| 🌪 | **Lokalna burza piaskowa** | −15 energii (±20%) |
| ⛰ | **Osunięcie skał** | Cofnięcie o losowe pole |
| 📶 | **Wzmocnienie anteny** | Ujawnienie celu misji |
| 🔋 | **Zapasowe ogniwa** | +20 energii |
| 💻 | **Błąd systemu** | −10 energii |
| 📳 | **Wstrząs sejsmiczny** | Losowe przesunięcie łazika |

Szansa zdarzenia w każdym kroku: **15% (easy) / 25% (normal) / 40% (hard)**.

---

## 🏆 System punktacji

```
Wynik = (Baza + Energia + Kroki + Sygnały) × Mnożnik trudności
```

| Składnik | Wartość |
|---|---|
| Baza za sukces | 500 pkt |
| Baza za częściowy sukces | 167 pkt |
| Za każdą pozostałą energię | +2 pkt |
| Za każdy niewykorzystany krok | +10 pkt |
| Za każdy zebrany sygnał | +100 pkt |
| Kara za porażkę | −200 pkt |

**Mnożnik trudności:**

| Poziom | Mnożnik |
|---|---|
| easy | ×1.0 |
| normal | ×1.5 |
| hard | ×2.5 |

---

## 🏁 Warunki zakończenia

Program implementuje **3 warunki zakończenia** (wymagane minimum: 2):

| # | Warunek | Wynik |
|---|---|---|
| 1 | **Wyczerpanie energii** (energia = 0) | ✘ Porażka |
| 2 | **Limit kroków** bez zebrania sygnałów | ✘ Porażka |
| 2b | **Limit kroków** z zebranymi sygnałami | ~ Częściowy sukces |
| 3 | **Dotarcie do celu misji** (sygnał główny) | ✔ Sukces |

---

## 📚 Biblioteka `lib.py`

Własna biblioteka terminalna napisana od zera. Przykłady użycia:

```python
import lib as L

# Kolory podstawowe
print(L.red("Błąd!"))
print(L.green("OK!"))
print(L.bold_yellow("Uwaga!"))

# True Color RGB
print(L.rgb(255, 120, 50, "Pomarańczowy tekst"))
print(L.rgb_bg(30, 30, 100, "Tekst na niebieskim tle"))

# Znaczniki
print(L.ok("Operacja zakończona"))
print(L.err("Coś poszło nie tak"))
print(L.warn("Sprawdź dane"))
print(L.info("Informacja"))
print(L.event("Zdarzenie!"))

# Pasek postępu
bar = L.progress_bar(value=75, maximum=100, width=20, label="Energia")
print(bar)   # Energia [███████████████░░░░░]  75/100

# Ramka
L.box("TYTUŁ", ["Linia 1", "Linia 2"], color_fn=L.bright_cyan)

# Animacje
L.typewrite("Tekst pojawia się powoli...", delay=0.05)
L.spinner("Ładowanie", duration=2.0)
L.loading_bar("Postęp", steps=30, delay=0.04)

# Input z walidacją
x = L.prompt_int("Podaj wartość", lo=0, hi=100, default=50)
choice = L.prompt_choice("Opcja", choices=["tak", "nie"])
```

**Automatyczne wykrywanie wsparcia kolorów:**
- `NO_COLOR=1` — wyłącz kolory
- `FORCE_COLOR=1` — wymuś kolory
- Windows: automatyczna aktywacja VT przez `ctypes`

---

## ⚙️ Konfiguracja `config.py`

Możesz dostosować zachowanie gry edytując `config.py`:

```python
# Zmień granice świata
WORLD_MIN = -100
WORLD_MAX =  100

# Zmień koszt ruchu
ENERGY_MOVE_COST = 5

# Dostosuj trudność
DIFFICULTY_SETTINGS["hard"]["event_chance"] = 0.6

# Dodaj własne zdarzenie
EVENTS.append({
    "id":     "alien_contact",
    "name":   "Kontakt z obcymi",
    "desc":   "Tajemniczy sygnał z głębin kosmosu!",
    "effect": "energy",
    "value":  +25,
    "symbol": "👽",
    "color":  "bright_green",
})
```

---

## 📋 Wymagania

- **Python**: 3.11+
- **Moduły**: wyłącznie standardowa biblioteka (`sys`, `os`, `time`, `random`, `math`, `shutil`, `re`)
- **Zewnętrzne biblioteki**: **żadne**
- **Pliki**: 9 plików `.py` + `README.md` (łącznie < 200 kB)
- **Sieć**: program nie łączy się z Internetem

---

## 🔗 Repozytoria

| | Link |
|---|---|
| 📦 Oryginalne (Gitea) | [git.racis.dev/marceliracis/gigathon-2026](https://git.racis.dev/marceliracis/gigathon-2026) |
| 🪞 Mirror (GitHub) | [github.com/MarceliRacis/gigathon-2026](https://github.com/MarceliRacis/gigathon-2026) |

---

<div align="center">

**ARES-MISSION** — Gigathon 2026  
Marceli Racis  
Python 3.11 · Stdlib Only · Terminal UI

</div>