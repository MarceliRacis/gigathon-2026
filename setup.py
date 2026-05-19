"""
setup.py — Konfiguracja wstępna misji
=======================================
Zbiera od użytkownika parametry startowe wyprawy.
Waliduje dane i zwraca gotowe obiekty Rover, World, EventEngine.
"""

from __future__ import annotations
import random
import lib as L
import display as D
from rover   import Rover
from world   import World
from event_engine import EventEngine
from config  import (
    DEFAULT_ROVER_NAME, DEFAULT_START_X, DEFAULT_START_Y,
    DEFAULT_ENERGY, DEFAULT_MAX_STEPS, DEFAULT_DIFFICULTY,
    WORLD_MIN, WORLD_MAX, ENERGY_MAX,
    DIFFICULTY_SETTINGS,
)


def gather_parameters() -> tuple[Rover, World, EventEngine, int]:
    """
    Pyta użytkownika o parametry misji.
    Zwraca (rover, world, event_engine, max_steps).
    """
    L.separator("═", L.bright_blue)
    L.section("KONFIGURACJA MISJI")
    print()
    print(L.info("Podaj parametry nowej wyprawy. Wciśnij ENTER aby użyć wartości domyślnej."))
    print()

    # ── Nazwa łazika ──────────────────────────────────────────────────────────
    raw_name = L.prompt(
        f"Nazwa łazika {L.dim(f'(domyślnie: {DEFAULT_ROVER_NAME})')}"
    ).strip()
    rover_name = raw_name if raw_name else DEFAULT_ROVER_NAME
    # Ogranicz długość i usuń dziwne znaki
    rover_name = rover_name[:24].strip() or DEFAULT_ROVER_NAME
    print(L.ok(f"Nazwa: {L.bold_yellow(rover_name)}"))
    print()

    # ── Pozycja startowa X ────────────────────────────────────────────────────
    print(L.info(f"Pozycja startowa musi być w zakresie [{WORLD_MIN}, {WORLD_MAX}]."))
    start_x = L.prompt_int(
        "Pozycja startowa X",
        lo=WORLD_MIN, hi=WORLD_MAX, default=DEFAULT_START_X,
    )
    start_y = L.prompt_int(
        "Pozycja startowa Y",
        lo=WORLD_MIN, hi=WORLD_MAX, default=DEFAULT_START_Y,
    )
    print(L.ok(f"Pozycja startowa: {L.coord_str(start_x, start_y)}"))
    print()

    # ── Energia startowa ──────────────────────────────────────────────────────
    print(L.info(f"Energia decyduje o wytrzymałości łazika. Max: {ENERGY_MAX}."))
    start_energy = L.prompt_int(
        "Energia startowa",
        lo=10, hi=ENERGY_MAX, default=DEFAULT_ENERGY,
    )
    print(L.ok(f"Energia startowa: {L.progress_bar(start_energy, ENERGY_MAX, 20)}"))
    print()

    # ── Poziom trudności ──────────────────────────────────────────────────────
    print(L.info("Poziom trudności wpływa na zdarzenia, liczbę pól i mnożnik wyniku."))
    print(f"  {L.bright_green('easy')}   — mniej zagrożeń, więcej bonusów")
    print(f"  {L.bright_yellow('normal')} — balans (domyślnie)")
    print(f"  {L.bright_red('hard')}   — więcej zagrożeń, wyższy mnożnik punktów")
    difficulty = L.prompt_choice(
        "Poziom trudności",
        choices=["easy", "normal", "hard"],
    )
    cfg = DIFFICULTY_SETTINGS[difficulty]
    print(L.ok(f"Poziom trudności: {L.bold_white(cfg['label'])}"))
    print()

    # ── Maks. liczba kroków ───────────────────────────────────────────────────
    print(L.info("Maksymalna liczba kroków to limit czasu misji."))
    bonus = cfg["max_steps_bonus"]
    default_steps = DEFAULT_MAX_STEPS + bonus
    max_steps = L.prompt_int(
        "Maks. liczba kroków",
        lo=5, hi=100, default=default_steps,
    )
    print(L.ok(f"Limit kroków: {L.bright_white(str(max_steps))}"))
    print()

    # ── Seed (opcjonalny) ─────────────────────────────────────────────────────
    raw_seed = L.prompt(
        f"Seed generatora świata {L.dim('(ENTER = losowy)')}"
    ).strip()
    seed: int | None = None
    if raw_seed:
        try:
            seed = int(raw_seed)
            print(L.ok(f"Seed: {L.dim(str(seed))}"))
        except ValueError:
            print(L.warn("Nieprawidłowy seed — użyto losowego."))
    else:
        print(L.dim("  Seed: losowy"))
    print()

    # ── Budowanie obiektów ────────────────────────────────────────────────────
    L.spinner("  Generowanie powierzchni Marsa...", duration=1.2)
    world = World(difficulty=difficulty, seed=seed)
    print(L.ok("Mapa wygenerowana!"))

    rover = Rover(
        name=rover_name,
        start_x=start_x,
        start_y=start_y,
        energy=start_energy,
        difficulty=difficulty,
    )

    engine = EventEngine(difficulty=difficulty)

    # Wyświetl informacje o świecie
    print()
    D.show_world_info(world)

    return rover, world, engine, max_steps