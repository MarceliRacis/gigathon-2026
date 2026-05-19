"""
rover.py — Klasa łazika ARES
============================
Przechowuje stan łazika: pozycję, energię, historię ruchu.
Obsługuje ruch, granice świata i zużycie energii.
"""

from __future__ import annotations
import math
from config import (
    WORLD_MIN, WORLD_MAX,
    ENERGY_MOVE_COST, ENERGY_MIN, ENERGY_MAX,
    DIFFICULTY_SETTINGS,
)


class Rover:
    """Reprezentuje łazika na powierzchni Marsa."""

    # Kierunki ruchu: nazwa → (dx, dy)
    DIRECTIONS: dict[str, tuple[int, int]] = {
        "n":  ( 0,  1),
        "s":  ( 0, -1),
        "e":  ( 1,  0),
        "w":  (-1,  0),
        "ne": ( 1,  1),
        "nw": (-1,  1),
        "se": ( 1, -1),
        "sw": (-1, -1),
    }

    DIRECTION_NAMES: dict[str, str] = {
        "n":  "Północ",
        "s":  "Południe",
        "e":  "Wschód",
        "w":  "Zachód",
        "ne": "Północny-Wschód",
        "nw": "Północny-Zachód",
        "se": "Południowy-Wschód",
        "sw": "Południowy-Zachód",
    }

    def __init__(
        self,
        name: str,
        start_x: int,
        start_y: int,
        energy: int,
        difficulty: str,
    ) -> None:
        self.name:       str   = name
        self.x:          int   = start_x
        self.y:          int   = start_y
        self.energy:     int   = min(energy, ENERGY_MAX)
        self.difficulty: str   = difficulty
        self.step:       int   = 0

        # Historia — lista słowników z informacjami o każdym kroku
        self.history: list[dict] = []

        # Statystyki
        self.total_distance:   float = 0.0
        self.craters_avoided:  int   = 0
        self.signals_found:    int   = 0
        self.events_survived:  int   = 0
        self.energy_collected: int   = 0

        # Pozycja startowa
        self.start_x: int = start_x
        self.start_y: int = start_y
        self.start_energy: int = energy

    # ──────────────────────────────────────────────────────────────────────────
    #  WŁAŚCIWOŚCI
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        return self.energy > ENERGY_MIN

    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def energy_pct(self) -> float:
        return self.energy / ENERGY_MAX

    # ──────────────────────────────────────────────────────────────────────────
    #  RUCH
    # ──────────────────────────────────────────────────────────────────────────

    def move(self, direction: str) -> dict:
        """
        Przesuwa łazika w podanym kierunku.
        Zwraca słownik z informacjami o ruchu:
          - moved (bool): czy ruch się udał
          - old_pos, new_pos (tuple)
          - energy_used (int)
          - reason (str): przyczyna nieudanego ruchu
          - boundary_hit (bool)
        """
        direction = direction.lower().strip()
        result = {
            "moved":        False,
            "old_pos":      (self.x, self.y),
            "new_pos":      (self.x, self.y),
            "energy_used":  0,
            "reason":       "",
            "boundary_hit": False,
        }

        if direction not in self.DIRECTIONS:
            result["reason"] = f"Nieznany kierunek: '{direction}'"
            return result

        if not self.is_alive:
            result["reason"] = "Brak energii — łazik unieruchomiony."
            return result

        dx, dy = self.DIRECTIONS[direction]
        new_x  = self.x + dx
        new_y  = self.y + dy

        # Sprawdzenie granic świata
        if not (WORLD_MIN <= new_x <= WORLD_MAX and WORLD_MIN <= new_y <= WORLD_MAX):
            result["reason"]       = "Granica obszaru badań — ruch zablokowany."
            result["boundary_hit"] = True
            # Koszt energii za próbę wyjścia poza granicę
            self._use_energy(1)
            result["energy_used"] = 1
            return result

        # Udany ruch
        old_x, old_y = self.x, self.y
        self.x = new_x
        self.y = new_y
        self._use_energy(ENERGY_MOVE_COST)

        dist = math.sqrt(dx**2 + dy**2)
        self.total_distance += dist

        result.update({
            "moved":       True,
            "old_pos":     (old_x, old_y),
            "new_pos":     (self.x, self.y),
            "energy_used": ENERGY_MOVE_COST,
            "reason":      "",
        })
        return result

    def force_move(self, dx: int, dy: int) -> None:
        """Wymuszony ruch (zdarzenia losowe) — nie kosztuje energii, respektuje granice."""
        new_x = max(WORLD_MIN, min(WORLD_MAX, self.x + dx))
        new_y = max(WORLD_MIN, min(WORLD_MAX, self.y + dy))
        self.total_distance += math.sqrt((new_x - self.x)**2 + (new_y - self.y)**2)
        self.x = new_x
        self.y = new_y

    def push_back(self, old_x: int, old_y: int) -> None:
        """Cofa łazika do poprzedniej pozycji (np. krater, osunięcie)."""
        self.x = old_x
        self.y = old_y

    # ──────────────────────────────────────────────────────────────────────────
    #  ENERGIA
    # ──────────────────────────────────────────────────────────────────────────

    def _use_energy(self, amount: int) -> None:
        self.energy = max(ENERGY_MIN, self.energy - amount)

    def add_energy(self, amount: int) -> int:
        """Dodaje energię (nie przekracza ENERGY_MAX). Zwraca faktycznie dodaną ilość."""
        before = self.energy
        self.energy = min(ENERGY_MAX, self.energy + amount)
        gained = self.energy - before
        if gained > 0:
            self.energy_collected += gained
        return gained

    def drain_energy(self, amount: int) -> int:
        """Odbiera energię. Zwraca faktycznie odjętą ilość."""
        before = self.energy
        self._use_energy(amount)
        return before - self.energy

    # ──────────────────────────────────────────────────────────────────────────
    #  HISTORIA
    # ──────────────────────────────────────────────────────────────────────────

    def log_step(self, entry: dict) -> None:
        """Dodaje wpis do historii kroków."""
        self.history.append(entry)

    # ──────────────────────────────────────────────────────────────────────────
    #  ODLEGŁOŚĆ OD PUNKTU
    # ──────────────────────────────────────────────────────────────────────────

    def distance_to(self, tx: int, ty: int) -> float:
        return math.sqrt((self.x - tx)**2 + (self.y - ty)**2)

    # ──────────────────────────────────────────────────────────────────────────
    #  REPRESENTACJA
    # ──────────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Rover(name={self.name!r}, pos=({self.x},{self.y}), "
            f"energy={self.energy}, step={self.step})"
        )