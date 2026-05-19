"""
config.py — Konfiguracja i stałe symulacji łazika ARES
=======================================================
Wszystkie magiczne liczby w jednym miejscu.
"""

# ─────────────────────── granice świata ──────────────────────────────────────
WORLD_MIN: int = -50
WORLD_MAX: int =  50

# ─────────────────────── domyślne parametry łazika ───────────────────────────
DEFAULT_ROVER_NAME:   str   = "ARES-1"
DEFAULT_START_X:      int   = 0
DEFAULT_START_Y:      int   = 0
DEFAULT_ENERGY:       int   = 100
DEFAULT_MAX_STEPS:    int   = 30
DEFAULT_DIFFICULTY:   str   = "normal"   # easy / normal / hard

# ─────────────────────── zasoby ──────────────────────────────────────────────
ENERGY_MOVE_COST:     int   = 3     # koszt energii za jeden ruch
ENERGY_MIN:           int   = 0     # minimalna energia → koniec gry
ENERGY_MAX:           int   = 100   # maksymalna energia (bufor)

# ─────────────────────── cel wyprawy ─────────────────────────────────────────
# Cel jest generowany losowo przy starcie (patrz world.py)
GOAL_SIGNAL_RADIUS:   int   = 3     # odległość do uznania dotarcia do sygnału

# ─────────────────────── poziomy trudności ───────────────────────────────────
DIFFICULTY_SETTINGS: dict = {
    "easy": {
        "label":             "ŁATWY 🟢",
        "event_chance":      0.15,   # szansa na zdarzenie losowe w kroku
        "dust_penalty":      8,
        "crater_penalty":    0,      # krater blokuje (cofa), bez kary energii
        "ice_bonus":         15,
        "signal_bonus":      20,
        "max_steps_bonus":   10,     # dodatkowe kroki vs default
    },
    "normal": {
        "label":             "NORMALNY 🟡",
        "event_chance":      0.25,
        "dust_penalty":      12,
        "crater_penalty":    0,
        "ice_bonus":         10,
        "signal_bonus":      15,
        "max_steps_bonus":   0,
    },
    "hard": {
        "label":             "TRUDNY 🔴",
        "event_chance":      0.40,
        "dust_penalty":      18,
        "crater_penalty":    5,      # krater dodatkowo kosztuje energię
        "ice_bonus":         7,
        "signal_bonus":      10,
        "max_steps_bonus":   -5,     # mniej kroków
    },
}

# ─────────────────────── typy pól świata ─────────────────────────────────────
FIELD_NORMAL  = "NORMAL"   # zwykły teren
FIELD_DUST    = "DUST"     # burza pyłowa
FIELD_ICE     = "ICE"      # pokłady lodu
FIELD_CRATER  = "CRATER"   # krater
FIELD_SIGNAL  = "SIGNAL"   # źródło sygnału (cel misji)
FIELD_ROCK    = "ROCK"     # skała — nie do przejścia

FIELD_INFO: dict = {
    FIELD_NORMAL:  {"symbol": "·",  "name": "Równina",       "color": "dim"},
    FIELD_DUST:    {"symbol": "💨", "name": "Burza pyłowa",  "color": "yellow"},
    FIELD_ICE:     {"symbol": "❄",  "name": "Pokład lodu",   "color": "cyan"},
    FIELD_CRATER:  {"symbol": "🕳", "name": "Krater",        "color": "red"},
    FIELD_SIGNAL:  {"symbol": "📡", "name": "Sygnał",        "color": "magenta"},
    FIELD_ROCK:    {"symbol": "🪨", "name": "Skała",         "color": "bright_black"},
}

# ─────────────────────── zdarzenia losowe ────────────────────────────────────
EVENTS: list[dict] = [
    {
        "id":      "solar_flare",
        "name":    "Rozbłysk słoneczny",
        "desc":    "Intensywne promieniowanie słoneczne laduje panele słoneczne!",
        "effect":  "energy",
        "value":   +12,
        "symbol":  "☀",
        "color":   "bright_yellow",
    },
    {
        "id":      "sand_storm",
        "name":    "Lokalna burza piaskowa",
        "desc":    "Gwałtowna burza uderza w łazika. Panele uszkodzone.",
        "effect":  "energy",
        "value":   -15,
        "symbol":  "🌪",
        "color":   "bright_red",
    },
    {
        "id":      "rock_slide",
        "name":    "Osunięcie skał",
        "desc":    "Odłamki skalne blokują trasę. Łazik musi się cofnąć.",
        "effect":  "pushback",
        "value":   0,
        "symbol":  "⛰",
        "color":   "red",
    },
    {
        "id":      "antenna_boost",
        "name":    "Wzmocnienie anteny",
        "desc":    "Łazik znalazł punkt wzmocnienia sygnału. Cel wykryty wyraźniej!",
        "effect":  "reveal_goal",
        "value":   0,
        "symbol":  "📶",
        "color":   "bright_cyan",
    },
    {
        "id":      "battery_find",
        "name":    "Zapasowe ogniwa",
        "desc":    "Pod skałą ukryto zapasowy pakiet baterii poprzedniej misji!",
        "effect":  "energy",
        "value":   +20,
        "symbol":  "🔋",
        "color":   "bright_green",
    },
    {
        "id":      "system_error",
        "name":    "Błąd systemu",
        "desc":    "Awaria komputera pokładowego. Restart zajął energię.",
        "effect":  "energy",
        "value":   -10,
        "symbol":  "💻",
        "color":   "bright_red",
    },
    {
        "id":      "seismic",
        "name":    "Wstrząs sejsmiczny",
        "desc":    "Marsjotrzęsienie! Łazik przesunięty losowo o 1 pole.",
        "effect":  "random_move",
        "value":   0,
        "symbol":  "📳",
        "color":   "bright_magenta",
    },
]

# ─────────────────────── wynik końcowy ───────────────────────────────────────
# Wynik = punkty za sukces + energia pozostała + bonus trudności - kary
SCORE_SUCCESS_BASE:  int = 500
SCORE_PER_ENERGY:    int = 2     # punkty za każdą pozostałą jednostkę energii
SCORE_PER_STEP_LEFT: int = 10    # punkty za każdy niewykorzystany krok
SCORE_SIGNAL_BONUS:  int = 100   # za zebranie sygnału (cel)
SCORE_FAIL_PENALTY:  int = -200  # kara za porażkę (obliczana oddzielnie)

DIFFICULTY_SCORE_MULTIPLIER: dict = {
    "easy":   1.0,
    "normal": 1.5,
    "hard":   2.5,
}