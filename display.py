"""
display.py — Moduł wyświetlania
================================
Wszystkie funkcje odpowiedzialne za wypisywanie informacji w terminalu.
Korzysta z lib.py do kolorowania i formatowania.
"""

from __future__ import annotations
import time
import lib as L
from config import (
    WORLD_MIN, WORLD_MAX,
    ENERGY_MAX, DIFFICULTY_SETTINGS, FIELD_INFO,
    FIELD_NORMAL, FIELD_DUST, FIELD_ICE, FIELD_CRATER, FIELD_SIGNAL, FIELD_ROCK,
)

# ─────────────────────── SPLASH / INTRO ──────────────────────────────────────

LOGO = r"""
     _    ____  _____ ____        __  __ ___ ____  ____ ___ ___  _   _
    / \  |  _ \| ____/ ___|      |  \/  |_ _/ ___/ ___|_ _/ _ \| \ | |
   / _ \ | |_) |  _| \___ \ _____| |\/| || |\___ \___ \| | | | |  \| |
  / ___ \|  _ <| |___ ___) |_____| |  | || | ___) |__) | | |_| | |\  |
 /_/   \_|_| \_|_____|____/      |_|  |_|___|____/____/___\___/|_| \_|
"""


def splash_screen() -> None:
    """Ekran powitalny z logo."""
    print()
    L.separator("═", L.bright_red)
    for line in LOGO.splitlines():
        print(L.bold(L.rgb(255, 120, 50, line)))
    print()
    subtitle = "  Symulator Misji Marsjańskiego Łazika  —  Python Edition"
    print(L.bold_cyan(subtitle.center(L.terminal_width())))
    author_line = "  Oparty wyłącznie na bibliotece standardowej Python 3.11+"
    print(L.dim(author_line.center(L.terminal_width())))
    L.separator("═", L.bright_red)
    print()
    L.typewrite(
        L.bright_cyan("  Inicjalizacja systemów łazika..."),
        delay=0.02,
    )
    L.loading_bar("  Ładowanie danych misji", steps=25, delay=0.03)
    print()


def mission_briefing() -> None:
    """Krótki briefing misji przed podaniem parametrów."""
    lines = [
        L.bold_white("MISJA: ARES-MISSION"),
        "",
        L.cyan("Twoim zadaniem jest sterowanie łazikiem na powierzchni Marsa."),
        L.cyan("Zbierz sygnały telemetryczne i wróć zanim skończy się energia."),
        "",
        L.bright_yellow("► Kieruj łazika poleceniami: N S E W NE NW SE SW"),
        L.bright_yellow("► Uważaj na burze pyłowe, kratery i skały!"),
        L.bright_yellow("► Pokłady lodu uzupełniają energię — szukaj ich!"),
        L.bright_yellow("► Zbierz sygnał (📡) aby ukończyć misję z sukcesem."),
        "",
        L.dim("Powodzenia, astronauto."),
    ]
    L.box("BRIEFING MISJI", lines, color_fn=L.bright_red, title_fn=L.bold_yellow)
    print()


def show_world_info(world) -> None:
    """Wyświetla informacje o świecie po generacji."""
    stats = world.stats()
    w     = L.terminal_width()

    L.section("DANE ŚRODOWISKA")
    print(L.info(f"Ziarno generatora świata (seed): {L.bright_yellow(str(stats['seed']))}"))
    print(L.info(f"Granice obszaru badań: X ∈ [{WORLD_MIN}, {WORLD_MAX}], Y ∈ [{WORLD_MIN}, {WORLD_MAX}]"))
    print(L.info(f"Cel misji (sygnał główny): {L.bright_magenta(str(stats['goal']))}"))
    print()

    # Legenda pól
    legend_lines = []
    field_map = {
        FIELD_DUST:   ("💨", "Burza pyłowa",  L.bright_yellow),
        FIELD_ICE:    ("❄",  "Pokład lodu",   L.bright_cyan),
        FIELD_CRATER: ("🕳", "Krater",        L.bright_red),
        FIELD_ROCK:   ("🪨", "Skała",         L.dim),
        FIELD_SIGNAL: ("📡", "Sygnał",        L.bright_magenta),
    }
    for ftype, (sym, fname, cfn) in field_map.items():
        cnt = stats["fields"].get(ftype, 0)
        legend_lines.append(f"  {sym}  {cfn(fname):<20} ({cnt} na mapie)")

    L.box("LEGENDA ŚWIATA", legend_lines, color_fn=L.cyan)
    print()


def show_parameters(rover, world, max_steps: int) -> None:
    """Wyświetla parametry startowe wyprawy."""
    cfg = DIFFICULTY_SETTINGS[rover.difficulty]
    dist = world.distance_to_goal(rover.x, rover.y)

    lines = [
        f"  Nazwa łazika   : {L.bold_yellow(rover.name)}",
        f"  Pozycja startowa: {L.coord_str(rover.x, rover.y)}",
        f"  Energia startowa: {L.progress_bar(rover.energy, ENERGY_MAX, 25)}",
        f"  Maks. kroków    : {L.bright_white(str(max_steps))}",
        f"  Poziom trudności: {L.bold_white(cfg['label'])}",
        f"  Koszt ruchu     : {L.bright_red(str(3))} energii/krok",
        f"  Odległość do celu: ~{L.bright_magenta(f'{dist:.1f}')} pól",
        f"  Cel ujawniony   : {'TAK' if world.goal_revealed else L.dim('NIE (zbierz sygnał anteny)')}",
    ]
    L.box("PARAMETRY WYPRAWY", lines, color_fn=L.bright_blue, title_fn=L.bold_white)
    print()


# ─────────────────────── KROK SYMULACJI ─────────────────────────────────────

def step_header(step: int, max_steps: int, rover) -> None:
    """Nagłówek kroku."""
    w   = L.terminal_width()
    bar = L.progress_bar(step, max_steps, width=15, color_fn=L.bright_cyan)
    pos = L.coord_str(rover.x, rover.y)
    eng = L.progress_bar(rover.energy, ENERGY_MAX, width=15)

    left  = L.bold_yellow(f"  KROK {step:>3}/{max_steps}")
    right = f"  Pos: {pos}  Energia: {eng}"

    # Separator z numerem kroku
    sep_char = "─"
    step_label = f"[ KROK {step} / {max_steps} ]"
    side = (w - len(step_label)) // 2
    print()
    print(L.bright_cyan(sep_char * side) + L.bold_yellow(step_label) + L.bright_cyan(sep_char * side))
    print(f"  {L.dim('Pozycja:')} {pos}   {L.dim('Energia:')} {eng}")


def show_direction_menu(world, rover) -> None:
    """Wyświetla menu wyboru kierunku z podpowiedzią."""
    dist  = world.distance_to_goal(rover.x, rover.y)
    hint  = world.hint_direction(rover.x, rover.y)

    print()
    directions_row1 = (
        f"  {L.bg_black(L.bright_white('NW'))}"
        f"  {L.bg_black(L.bright_white(' N'))}"
        f"  {L.bg_black(L.bright_white('NE'))}"
    )
    directions_row2 = (
        f"  {L.bg_black(L.bright_white(' W'))}"
        f"  {L.dim('  ●')}"
        f"  {L.bg_black(L.bright_white(' E'))}"
    )
    directions_row3 = (
        f"  {L.bg_black(L.bright_white('SW'))}"
        f"  {L.bg_black(L.bright_white(' S'))}"
        f"  {L.bg_black(L.bright_white('SE'))}"
    )

    print(L.dim("  ┌─────────────────────────────────────────────────────┐"))
    print(L.dim("  │") + L.bold_cyan("  Kierunki ruchu:") + " " * 36 + L.dim("│"))
    print(L.dim("  │") + "   NW  N  NE  |  W  ●  E  |  SW  S  SE         " + L.dim("│"))
    if world.goal_revealed:
        hint_str = L.bright_magenta(f"Cel: {hint}")
    else:
        hint_str = L.dim("Cel: nieznany (szukaj sygnału anteny 📶)")
    pad = 50 - len(hint) - 5
    print(L.dim("  │") + f"  {hint_str}" + " " * max(0, 45) + L.dim("│"))
    print(L.dim("  │") + f"  {L.dim('Dystans do celu:')} {L.bright_magenta(f'{dist:.1f} pól')}" + " " * 30 + L.dim("│"))
    print(L.dim("  └─────────────────────────────────────────────────────┘"))
    print()


def show_move_result(move_result: dict, energy_before: int, rover) -> None:
    """Wyświetla wynik ruchu."""
    if move_result["moved"]:
        old = move_result["old_pos"]
        new = move_result["new_pos"]
        cost = move_result["energy_used"]
        print(L.ok(
            f"Ruch: {L.coord_str(*old)} → {L.coord_str(*new)}"
            f"  {L.dim('(koszt:')} {L.bright_red(str(cost))} {L.dim('energii)')}"
        ))
    elif move_result["boundary_hit"]:
        print(L.warn("Granica obszaru badań! Ruch zablokowany."))
    else:
        print(L.err(move_result["reason"]))


def show_field_effect(effect: dict | None) -> None:
    """Wyświetla efekt pola."""
    if effect is None:
        print(L.dim("  · Teren normalny — brak specjalnych efektów."))
        return

    sym  = effect.get("symbol", "?")
    name = effect.get("name",   "Nieznane pole")
    desc = effect.get("desc",   "")
    eff  = effect.get("effect", "")

    delta = effect.get("energy_delta", 0)
    if delta > 0:
        col = L.bright_green
    elif delta < 0:
        col = L.bright_red
    else:
        col = L.bright_yellow

    print(L.event(f"{sym}  {col(name)}"))
    print(L.arrow(desc))
    print(L.arrow(f"Efekt: {col(eff)}"))


def show_event(event: dict, result: str) -> None:
    """Wyświetla zdarzenie losowe."""
    sym  = event.get("symbol", "★")
    name = event.get("name",   "Zdarzenie")
    desc = event.get("desc",   "")

    print()
    L.separator("·", L.bright_magenta)
    print(L.bold_magenta(f"  {sym}  ZDARZENIE LOSOWE: {name.upper()}"))
    print(L.arrow(desc))
    print(L.arrow(f"Skutek: {L.bright_yellow(result)}"))
    L.separator("·", L.bright_magenta)


# ─────────────────────── ZAKOŃCZENIE ────────────────────────────────────────

def show_end_screen(outcome: str) -> None:
    """Ekran końca gry — sukces / porażka."""
    print()
    if outcome == "success":
        L.separator("★", L.bright_green)
        print(L.bold_green("  ✔  MISJA ZAKOŃCZONA SUKCESEM!".center(L.terminal_width())))
        print(L.bright_green("  Dane telemetryczne bezpiecznie przesłane do bazy na Ziemi.".center(L.terminal_width())))
        L.separator("★", L.bright_green)
    elif outcome == "partial":
        L.separator("~", L.bright_yellow)
        print(L.bold_yellow("  ~  CZĘŚCIOWY SUKCES".center(L.terminal_width())))
        print(L.bright_yellow("  Łazik wrócił, ale nie wszystkie dane zostały zebrane.".center(L.terminal_width())))
        L.separator("~", L.bright_yellow)
    else:
        L.separator("✘", L.bright_red)
        print(L.bold_red("  ✘  MISJA ZAKOŃCZONA NIEPOWODZENIEM".center(L.terminal_width())))
        print(L.bright_red("  Łazik utracił zasilanie lub przekroczył limit misji.".center(L.terminal_width())))
        L.separator("✘", L.bright_red)
    print()


def show_report(report: dict) -> None:
    """Drukuje szczegółowy raport końcowy misji."""
    r = report

    L.header("RAPORT KOŃCOWY MISJI")
    print()

    # Sekcja 1: Parametry
    L.section("PARAMETRY STARTOWE")
    params = [
        f"  Nazwa łazika      : {L.bold_yellow(r['rover_name'])}",
        f"  Pozycja startowa  : {L.coord_str(*r['start_pos'])}",
        f"  Energia startowa  : {L.bright_white(str(r['start_energy']))}",
        f"  Poziom trudności  : {L.bold_white(r['difficulty_label'])}",
        f"  Maks. kroków      : {L.bright_white(str(r['max_steps']))}",
        f"  Seed świata       : {L.dim(str(r['world_seed']))}",
    ]
    for p in params: print(p)
    print()

    # Sekcja 2: Wyniki
    L.section("WYNIKI WYPRAWY")
    results = [
        f"  Końcowa pozycja   : {L.coord_str(*r['final_pos'])}",
        f"  Wykonane kroki    : {L.bright_white(str(r['steps_taken']))} / {r['max_steps']}",
        f"  Pokonany dystans  : {L.bright_white('{:.1f}'.format(r['total_distance']))} pól",
        f"  Pozostała energia : {L.progress_bar(r['energy_left'], ENERGY_MAX, 20)}",
        f"  Zbrane sygnały    : {L.bright_magenta(str(r['signals_found']))}",
        f"  Przeżyte zdarzenia: {L.bright_cyan(str(r['events_survived']))}",
        f"  Kraterate wykryte : {L.bright_red(str(r['craters_hit']))}",
    ]
    for res in results: print(res)
    print()

    # Sekcja 3: Zdarzenia
    if r["event_log"]:
        L.section("HISTORIA ZDARZEŃ")
        for i, ev in enumerate(r["event_log"], 1):
            sym    = ev.get("symbol", "★")
            name   = ev.get("name", "?")
            step   = ev.get("step", "?")
            result = ev.get("applied_result", "")
            print(f"  {L.dim(str(i)+'. ')}Krok {L.bright_white(str(step))}: {sym} {L.bright_magenta(name)} → {L.bright_yellow(result)}")
        print()

    # Sekcja 4: Przyczyna zakończenia
    L.section("PRZYCZYNA ZAKOŃCZENIA")
    reason_col = L.bright_green if r["outcome"] == "success" else L.bright_red
    print(f"  {reason_col(r['end_reason'])}")
    print()

    # Sekcja 5: Wynik punktowy
    L.section("WYNIK KOŃCOWY")
    score_bar = L.progress_bar(
        min(r["score"], 1000), 1000, width=30,
        color_fn=L.bright_green if r["score"] >= 500 else L.bright_yellow
    )
    print(f"  Punkty        : {L.bold_yellow(str(r['score']))} pkt")
    print(f"  Ocena         : {score_bar}")
    print(f"  Wynik misji   : {reason_col(r['outcome_label'].upper())}")
    print()

    L.separator("═", L.bright_cyan)
    print()