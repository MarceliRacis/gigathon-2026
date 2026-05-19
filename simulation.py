"""
simulation.py — Główna pętla symulacji
========================================
Łączy wszystkie moduły: łazik, świat, zdarzenia, wyświetlanie.
Obsługuje kroki, warunki zakończenia i oblicza wynik końcowy.
"""

from __future__ import annotations
import random
import time
import lib as L
import display as D
from rover  import Rover
from world  import World
from events import EventEngine
from config import (
    DIFFICULTY_SETTINGS,
    SCORE_SUCCESS_BASE, SCORE_PER_ENERGY, SCORE_PER_STEP_LEFT,
    SCORE_SIGNAL_BONUS, SCORE_FAIL_PENALTY,
    DIFFICULTY_SCORE_MULTIPLIER,
    ENERGY_MIN, ENERGY_MAX,
    FIELD_CRATER, FIELD_ROCK,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  KLASA SYMULACJI
# ═══════════════════════════════════════════════════════════════════════════════

class Simulation:
    """
    Zarządza przebiegiem całej symulacji.
    """

    def __init__(
        self,
        rover:     Rover,
        world:     World,
        engine:    EventEngine,
        max_steps: int,
    ) -> None:
        self.rover     = rover
        self.world     = world
        self.engine    = engine
        self.max_steps = max_steps

        self.running:     bool = True
        self.end_reason:  str  = ""
        self.outcome:     str  = "fail"   # success / partial / fail
        self.score:       int  = 0

        # Krótka lista kluczowych zdarzeń do raportu
        self.key_events: list[str] = []

    # ──────────────────────────────────────────────────────────────────────────
    #  GŁÓWNA PĘTLA
    # ──────────────────────────────────────────────────────────────────────────

    def run(self) -> dict:
        """
        Uruchamia pętlę symulacji.
        Zwraca słownik raportu końcowego.
        """
        D.show_parameters(self.rover, self.world, self.max_steps)
        L.pause(0.5)

        while self.running:
            self.rover.step += 1
            step = self.rover.step

            # ── Nagłówek kroku ──────────────────────────────────────────────
            D.step_header(step, self.max_steps, self.rover)
            D.show_direction_menu(self.world, self.rover)

            # ── Pobranie ruchu od użytkownika ────────────────────────────────
            direction = self._get_direction()
            energy_before = self.rover.energy

            # ── Wykonanie ruchu ──────────────────────────────────────────────
            old_pos = (self.rover.x, self.rover.y)

            # Sprawdź czy docelowe pole to skała (blokada z wyprzedzeniem)
            dx, dy = Rover.DIRECTIONS.get(direction, (0, 0))
            target_x = self.rover.x + dx
            target_y = self.rover.y + dy
            if not self.world.is_passable(target_x, target_y):
                print(L.warn(f"  🪨 Skała blokuje drogę na ({target_x}, {target_y})! Zmień kierunek."))
                # Koszt energii za nieudaną próbę
                self.rover.drain_energy(1)
                self._check_end_conditions(step)
                continue

            move_result = self.rover.move(direction)
            D.show_move_result(move_result, energy_before, self.rover)

            # ── Efekt pola ───────────────────────────────────────────────────
            field_effect = self.world.apply_field_effect(
                self.rover.x, self.rover.y,
                self.rover, self.rover.difficulty
            )

            # Krater → cofnięcie
            if field_effect and field_effect.get("pushback"):
                self.rover.push_back(*old_pos)
                print(L.warn(f"  Łazik cofnięty do {L.coord_str(*old_pos)}"))
                self.key_events.append(
                    f"Krok {step}: Krater na {L.coord_str(target_x, target_y)} — cofnięcie"
                )

            # Sygnał zebrany
            if field_effect and field_effect.get("signal_collected"):
                self.rover.signals_found += 0  # już zliczone w world.py
                self.key_events.append(
                    f"Krok {step}: Zebrany sygnał na {L.coord_str(self.rover.x, self.rover.y)}"
                )

            D.show_field_effect(field_effect)

            # ── Zdarzenie losowe ─────────────────────────────────────────────
            event = self.engine.roll(step)
            if event:
                result = self.engine.apply(event, self.rover, self.world)
                D.show_event(event, result)
                self.key_events.append(
                    f"Krok {step}: {event['name']} → {result}"
                )

            # ── Logowanie kroku ──────────────────────────────────────────────
            self.rover.log_step({
                "step":         step,
                "direction":    direction,
                "pos":          (self.rover.x, self.rover.y),
                "energy":       self.rover.energy,
                "field_effect": field_effect,
                "event":        event,
            })

            # ── Sprawdzenie warunków końcowych ───────────────────────────────
            self._check_end_conditions(step)

            L.pause(0.3)

        # ── Obliczenie wyniku i raport ───────────────────────────────────────
        self.score = self._calculate_score()
        return self._build_report()

    # ──────────────────────────────────────────────────────────────────────────
    #  WEJŚCIE OD UŻYTKOWNIKA
    # ──────────────────────────────────────────────────────────────────────────

    def _get_direction(self) -> str:
        """Pyta o kierunek, z obsługą błędów i podpowiedziami."""
        valid = list(Rover.DIRECTIONS.keys())
        while True:
            raw = L.prompt(
                L.bright_cyan("Kierunek") + L.dim(" [n/s/e/w/ne/nw/se/sw]")
            ).strip().lower()

            if raw in valid:
                dir_name = Rover.DIRECTION_NAMES.get(raw, raw.upper())
                print(L.arrow(f"Wybrano: {L.bright_yellow(dir_name)}"))
                return raw

            if raw in ("q", "quit", "exit"):
                print(L.warn("Przerwanie misji przez użytkownika."))
                self.running   = False
                self.end_reason = "Misja przerwana przez operatora."
                self.outcome   = "fail"
                return "n"   # dummy

            valid_str = "  ".join(L.bright_yellow(d) for d in valid)
            print(L.err(f"Nieprawidłowy kierunek '{raw}'. Dostępne: {valid_str}"))

    # ──────────────────────────────────────────────────────────────────────────
    #  WARUNKI KOŃCOWE
    # ──────────────────────────────────────────────────────────────────────────

    def _check_end_conditions(self, step: int) -> None:
        """
        Sprawdza co najmniej 2 warunki zakończenia:
        1. Brak energii
        2. Przekroczenie limitu kroków
        3. Dotarcie do celu misji (sygnał główny)
        """
        # Warunek 1: brak energii
        if self.rover.energy <= ENERGY_MIN:
            print()
            L.blink_message("  ⚡ KRYTYCZNY BRAK ENERGII — ŁAZIK UNIERUCHOMIONY!", times=2)
            self.end_reason = "Wyczerpanie energii — łazik utracił zasilanie."
            self.outcome    = "fail"
            self.running    = False
            return

        # Warunek 2: limit kroków
        if step >= self.max_steps:
            print()
            print(L.warn("  ⏱ Osiągnięto limit kroków misji."))
            if self.rover.signals_found > 0:
                self.end_reason = f"Limit kroków ({self.max_steps}) — zebrano {self.rover.signals_found} sygnał(y)."
                self.outcome    = "partial"
            else:
                self.end_reason = f"Limit kroków ({self.max_steps}) — brak zebranych sygnałów."
                self.outcome    = "fail"
            self.running = False
            return

        # Warunek 3: dotarcie do celu
        gx, gy = self.world.goal_pos
        dist   = self.rover.distance_to(gx, gy)
        if self.world.is_goal(self.rover.x, self.rover.y) or dist < 1.5:
            # Zbierz sygnał jeśli jeszcze nie zebrany
            if self.world.get_field(self.rover.x, self.rover.y) == "SIGNAL":
                pass  # już obsłużone przez apply_field_effect
            print()
            L.spinner("  Przesyłanie danych telemetrycznych...", duration=1.5)
            print(L.ok("  Dane przesłane! Cel misji osiągnięty!"))
            self.end_reason = f"Dotarcie do celu misji na {L.coord_str(gx, gy)}."
            self.outcome    = "success"
            self.running    = False
            return

    # ──────────────────────────────────────────────────────────────────────────
    #  OBLICZENIE WYNIKU
    # ──────────────────────────────────────────────────────────────────────────

    def _calculate_score(self) -> int:
        """
        Wynik = (base + energia + kroki + sygnały) × mnożnik trudności
        """
        multiplier = DIFFICULTY_SCORE_MULTIPLIER[self.rover.difficulty]

        if self.outcome == "success":
            base = SCORE_SUCCESS_BASE
        elif self.outcome == "partial":
            base = SCORE_SUCCESS_BASE // 3
        else:
            base = 0

        energy_pts  = self.rover.energy * SCORE_PER_ENERGY
        steps_left  = max(0, self.max_steps - self.rover.step)
        step_pts    = steps_left * SCORE_PER_STEP_LEFT
        signal_pts  = self.rover.signals_found * SCORE_SIGNAL_BONUS
        fail_pen    = SCORE_FAIL_PENALTY if self.outcome == "fail" else 0

        raw = base + energy_pts + step_pts + signal_pts + fail_pen
        score = int(max(0, raw) * multiplier)
        return score

    # ──────────────────────────────────────────────────────────────────────────
    #  RAPORT
    # ──────────────────────────────────────────────────────────────────────────

    def _build_report(self) -> dict:
        outcome_labels = {
            "success": "✔ SUKCES",
            "partial": "~ CZĘŚCIOWY SUKCES",
            "fail":    "✘ PORAŻKA",
        }
        cfg = DIFFICULTY_SETTINGS[self.rover.difficulty]

        return {
            # Parametry startowe
            "rover_name":       self.rover.name,
            "start_pos":        (self.rover.start_x, self.rover.start_y),
            "start_energy":     self.rover.start_energy,
            "difficulty_label": cfg["label"],
            "max_steps":        self.max_steps,
            "world_seed":       self.world.seed,

            # Wyniki
            "final_pos":        (self.rover.x, self.rover.y),
            "steps_taken":      self.rover.step,
            "total_distance":   self.rover.total_distance,
            "energy_left":      self.rover.energy,
            "signals_found":    self.rover.signals_found,
            "events_survived":  self.rover.events_survived,
            "craters_hit":      self.rover.craters_avoided,
            "event_log":        self.engine.summary(),
            "key_events":       self.key_events,

            # Zakończenie
            "end_reason":       self.end_reason,
            "outcome":          self.outcome,
            "outcome_label":    outcome_labels.get(self.outcome, self.outcome),
            "score":            self.score,
        }