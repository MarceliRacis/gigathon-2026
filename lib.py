"""
lib.py — Biblioteka terminalna łazika ARES
==========================================
Własna biblioteka do obsługi kolorów, stylów, ramek i animacji w terminalu.
Używa wyłącznie standardowej biblioteki Pythona (sys, os, time, shutil).
"""

import sys
import os
import time
import shutil


# ═══════════════════════════════════════════════════════════════════════════════
#  WYKRYWANIE OBSŁUGI KOLORÓW
# ═══════════════════════════════════════════════════════════════════════════════

def _supports_color() -> bool:
    """Sprawdza, czy terminal obsługuje kolory ANSI."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return True   # plik/pipe – i tak wyślij kody (można zobaczyć w less -R)
    platform = sys.platform
    if platform == "win32":
        # Windows 10+ obsługuje ANSI po włączeniu VT
        try:
            import ctypes
            kernel = ctypes.windll.kernel32          # type: ignore
            kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


COLOR_SUPPORT = _supports_color()


# ═══════════════════════════════════════════════════════════════════════════════
#  KODY ANSI
# ═══════════════════════════════════════════════════════════════════════════════

class _ANSI:
    RESET     = "\033[0m"
    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    ITALIC    = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK     = "\033[5m"
    REVERSE   = "\033[7m"
    STRIKE    = "\033[9m"

    # Kolory tekstu (foreground)
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    # Jasne kolory tekstu
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

    # Tła (background)
    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"

    BG_BRIGHT_BLACK   = "\033[100m"
    BG_BRIGHT_RED     = "\033[101m"
    BG_BRIGHT_GREEN   = "\033[102m"
    BG_BRIGHT_YELLOW  = "\033[103m"
    BG_BRIGHT_BLUE    = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN    = "\033[106m"
    BG_BRIGHT_WHITE   = "\033[107m"


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLICZNE FUNKCJE STYLIZACJI
# ═══════════════════════════════════════════════════════════════════════════════

def _c(code: str, text: str) -> str:
    """Opakowuje tekst kodem ANSI jeśli terminal to obsługuje."""
    if not COLOR_SUPPORT:
        return text
    return f"{code}{text}{_ANSI.RESET}"


# Skróty kolorów tekstu
def red(t: str)            -> str: return _c(_ANSI.RED,            t)
def green(t: str)          -> str: return _c(_ANSI.GREEN,          t)
def yellow(t: str)         -> str: return _c(_ANSI.YELLOW,         t)
def blue(t: str)           -> str: return _c(_ANSI.BLUE,           t)
def magenta(t: str)        -> str: return _c(_ANSI.MAGENTA,        t)
def cyan(t: str)           -> str: return _c(_ANSI.CYAN,           t)
def white(t: str)          -> str: return _c(_ANSI.WHITE,          t)
def bright_red(t: str)     -> str: return _c(_ANSI.BRIGHT_RED,     t)
def bright_green(t: str)   -> str: return _c(_ANSI.BRIGHT_GREEN,   t)
def bright_yellow(t: str)  -> str: return _c(_ANSI.BRIGHT_YELLOW,  t)
def bright_blue(t: str)    -> str: return _c(_ANSI.BRIGHT_BLUE,    t)
def bright_magenta(t: str) -> str: return _c(_ANSI.BRIGHT_MAGENTA, t)
def bright_cyan(t: str)    -> str: return _c(_ANSI.BRIGHT_CYAN,    t)
def bright_white(t: str)   -> str: return _c(_ANSI.BRIGHT_WHITE,   t)
def dim(t: str)            -> str: return _c(_ANSI.DIM,            t)

# Skróty stylów
def bold(t: str)      -> str: return _c(_ANSI.BOLD,      t)
def italic(t: str)    -> str: return _c(_ANSI.ITALIC,    t)
def underline(t: str) -> str: return _c(_ANSI.UNDERLINE, t)
def strike(t: str)    -> str: return _c(_ANSI.STRIKE,    t)

# Połączenia (bold + kolor)
def bold_red(t: str)     -> str: return _c(_ANSI.BOLD + _ANSI.RED,           t)
def bold_green(t: str)   -> str: return _c(_ANSI.BOLD + _ANSI.BRIGHT_GREEN,  t)
def bold_yellow(t: str)  -> str: return _c(_ANSI.BOLD + _ANSI.BRIGHT_YELLOW, t)
def bold_cyan(t: str)    -> str: return _c(_ANSI.BOLD + _ANSI.BRIGHT_CYAN,   t)
def bold_magenta(t: str) -> str: return _c(_ANSI.BOLD + _ANSI.BRIGHT_MAGENTA,t)
def bold_white(t: str)   -> str: return _c(_ANSI.BOLD + _ANSI.BRIGHT_WHITE,  t)

# Tła
def bg_red(t: str)    -> str: return _c(_ANSI.BG_RED    + _ANSI.BRIGHT_WHITE, t)
def bg_green(t: str)  -> str: return _c(_ANSI.BG_GREEN  + _ANSI.BRIGHT_WHITE, t)
def bg_yellow(t: str) -> str: return _c(_ANSI.BG_YELLOW + _ANSI.BLACK,        t)
def bg_blue(t: str)   -> str: return _c(_ANSI.BG_BLUE   + _ANSI.BRIGHT_WHITE, t)
def bg_cyan(t: str)   -> str: return _c(_ANSI.BG_CYAN   + _ANSI.BLACK,        t)
def bg_black(t: str)  -> str: return _c(_ANSI.BG_BLACK  + _ANSI.BRIGHT_WHITE, t)


def rgb(r: int, g: int, b: int, text: str) -> str:
    """Kolor 24-bit (True Color) — działa na większości nowoczesnych terminali."""
    if not COLOR_SUPPORT:
        return text
    return f"\033[38;2;{r};{g};{b}m{text}{_ANSI.RESET}"


def rgb_bg(r: int, g: int, b: int, text: str) -> str:
    """Tło 24-bit."""
    if not COLOR_SUPPORT:
        return text
    return f"\033[48;2;{r};{g};{b}m{text}{_ANSI.RESET}"


# ═══════════════════════════════════════════════════════════════════════════════
#  RAMKI I SEPARATORY
# ═══════════════════════════════════════════════════════════════════════════════

def terminal_width() -> int:
    """Zwraca szerokość terminala (domyślnie 80)."""
    return shutil.get_terminal_size((80, 24)).columns


def separator(char: str = "─", color_fn=None) -> None:
    """Drukuje poziomy separator na całą szerokość terminala."""
    w = terminal_width()
    line = char * w
    print(color_fn(line) if color_fn else line)


def box(title: str, lines: list[str], color_fn=None, title_fn=None) -> None:
    """
    Rysuje ramkę z tytułem i zawartością.
    
    Przykład:
    ╔══════════════╗
    ║  TYTUŁ       ║
    ╠══════════════╣
    ║  linia 1     ║
    ╚══════════════╝
    """
    w = terminal_width()
    inner = w - 4   # miejsce na ║ spacja ... spacja ║

    cf  = color_fn  or (lambda x: x)
    tf  = title_fn  or bold_yellow

    top    = cf("╔" + "═" * (w - 2) + "╗")
    sep    = cf("╠" + "═" * (w - 2) + "╣")
    bot    = cf("╚" + "═" * (w - 2) + "╝")
    side   = cf("║")

    title_str = tf(f" {title} ")
    # wyśrodkowanie tytułu (bez kodów ANSI do liczenia długości)
    visible_title = f" {title} "
    pad = max(0, inner - len(visible_title))
    left_pad  = pad // 2
    right_pad = pad - left_pad

    print(top)
    print(f"{side}{' ' * left_pad}{title_str}{' ' * right_pad}  {side}")
    print(sep)
    for line in lines:
        visible_len = _visible_length(line)
        padding = max(0, inner - visible_len)
        print(f"{side} {line}{' ' * padding} {side}")
    print(bot)


def header(text: str) -> None:
    """Duży nagłówek ASCII art."""
    w = terminal_width()
    separator("═", bright_cyan)
    centered = text.center(w)
    print(bold_cyan(centered))
    separator("═", bright_cyan)


def section(text: str) -> None:
    """Sekcja — mniejszy nagłówek."""
    w = terminal_width()
    line = f"  ▸ {text}  "
    pad  = "─" * max(0, w - len(line) - 2)
    print(bold_yellow(f"  ▸ {text}  ") + dim(pad))


# ═══════════════════════════════════════════════════════════════════════════════
#  IKONY / ZNACZNIKI
# ═══════════════════════════════════════════════════════════════════════════════

def ok(text: str)    -> str: return bold_green(f"  ✔ {text}")
def err(text: str)   -> str: return bold_red  (f"  ✘ {text}")
def warn(text: str)  -> str: return bold_yellow(f"  ⚠ {text}")
def info(text: str)  -> str: return bright_cyan(f"  ℹ {text}")
def event(text: str) -> str: return bright_magenta(f"  ★ {text}")
def arrow(text: str) -> str: return dim(f"  → {text}")


# ═══════════════════════════════════════════════════════════════════════════════
#  PASEK POSTĘPU
# ═══════════════════════════════════════════════════════════════════════════════

def progress_bar(value: float, maximum: float, width: int = 20,
                 label: str = "", color_fn=None) -> str:
    """
    Zwraca pasek postępu jako string.
    Przykład: [████████░░░░]  80/100
    """
    if maximum <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, value / maximum))

    filled = int(ratio * width)
    empty  = width - filled

    bar_inner = "█" * filled + "░" * empty
    cf = color_fn or (
        bright_green if ratio > 0.6 else
        bright_yellow if ratio > 0.3 else
        bright_red
    )
    bar = f"[{cf(bar_inner)}]"
    suffix = f"  {int(value)}/{int(maximum)}"
    if label:
        return f"{label} {bar}{suffix}"
    return f"{bar}{suffix}"


# ═══════════════════════════════════════════════════════════════════════════════
#  ANIMACJE / EFEKTY
# ═══════════════════════════════════════════════════════════════════════════════

def typewrite(text: str, delay: float = 0.03, newline: bool = True) -> None:
    """Efekt maszyny do pisania."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()


def spinner(message: str, duration: float = 1.0, delay: float = 0.1) -> None:
    """Animowany spinner przez określony czas."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = bright_cyan(frames[i % len(frames)])
        sys.stdout.write(f"\r  {frame}  {message}")
        sys.stdout.flush()
        time.sleep(delay)
        i += 1
    sys.stdout.write("\r" + " " * (len(message) + 8) + "\r")
    sys.stdout.flush()


def loading_bar(message: str, steps: int = 20, delay: float = 0.05) -> None:
    """Animowany pasek ładowania."""
    print()
    for i in range(steps + 1):
        ratio = i / steps
        filled = int(ratio * steps)
        bar = bright_green("█" * filled) + dim("░" * (steps - filled))
        pct = f"{int(ratio * 100):3d}%"
        sys.stdout.write(f"\r  {message}  [{bar}] {bright_yellow(pct)}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def blink_message(text: str, times: int = 3, delay: float = 0.3) -> None:
    """Migający komunikat (używaj oszczędnie)."""
    for _ in range(times):
        sys.stdout.write(f"\r{bold_red(text)}")
        sys.stdout.flush()
        time.sleep(delay)
        sys.stdout.write("\r" + " " * len(text))
        sys.stdout.flush()
        time.sleep(delay / 2)
    print(bold_red(text))


# ═══════════════════════════════════════════════════════════════════════════════
#  INPUT Z WALIDACJĄ
# ═══════════════════════════════════════════════════════════════════════════════

def prompt(text: str) -> str:
    """Kolorowy prompt."""
    return input(bold_cyan(f"  ▶ {text}: "))


def prompt_int(text: str, lo: int, hi: int, default: int) -> int:
    """
    Pyta o liczbę całkowitą w zakresie [lo, hi].
    Zwraca domyślną wartość przy błędzie.
    """
    raw = prompt(f"{text} [{lo}–{hi}, domyślnie {default}]")
    try:
        val = int(raw)
        if lo <= val <= hi:
            return val
        print(warn(f"Poza zakresem. Użyto domyślnej wartości: {default}"))
        return default
    except ValueError:
        if raw.strip() == "":
            return default
        print(warn(f"Nieprawidłowa wartość. Użyto domyślnej: {default}"))
        return default


def prompt_float(text: str, lo: float, hi: float, default: float) -> float:
    """Pyta o liczbę zmiennoprzecinkową."""
    raw = prompt(f"{text} [{lo}–{hi}, domyślnie {default}]")
    try:
        val = float(raw)
        if lo <= val <= hi:
            return val
        print(warn(f"Poza zakresem. Użyto domyślnej wartości: {default}"))
        return default
    except ValueError:
        if raw.strip() == "":
            return default
        print(warn(f"Nieprawidłowa wartość. Użyto domyślnej: {default}"))
        return default


def prompt_choice(text: str, choices: list[str]) -> str:
    """
    Pyta o wybór z listy opcji (case-insensitive).
    Zwraca pierwszą opcję przy błędzie.
    """
    choices_lower = [c.lower() for c in choices]
    choices_display = "/".join(bright_yellow(c) for c in choices)
    raw = prompt(f"{text} [{choices_display}]").strip().lower()
    if raw in choices_lower:
        return raw
    print(warn(f"Nieznana opcja. Wybrano: {choices[0]}"))
    return choices[0]


# ═══════════════════════════════════════════════════════════════════════════════
#  POMOCNICZE
# ═══════════════════════════════════════════════════════════════════════════════

def _visible_length(text: str) -> int:
    """Długość stringa bez kodów ANSI (do wyrównywania)."""
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return len(ansi_escape.sub('', text))


def clear_screen() -> None:
    """Czyści ekran terminala (opcjonalne, niewymagane)."""
    os.system("cls" if sys.platform == "win32" else "clear")


def pause(seconds: float = 0.6) -> None:
    """Krótka pauza dla czytelności."""
    time.sleep(seconds)


def coord_str(x: float, y: float) -> str:
    """Czytelna reprezentacja współrzędnych."""
    xs = f"{x:+.1f}" if isinstance(x, float) else f"{x:+d}"
    ys = f"{y:+.1f}" if isinstance(y, float) else f"{y:+d}"
    return bright_white(f"({xs}, {ys})")