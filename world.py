"""
world.py — Świat symulacji (mapa 2D)
=====================================
Generuje i przechowuje układ pól na mapie.
Obsługuje wykrywanie pól pod łazikiem oraz stosowanie ich efektów.
"""

from __future__ import annotations
import random
import math
from config import (
    WORLD_MIN, WORLD_MAX,
    FIELD_NORMAL, FIELD_DUST, FIELD_ICE,
    FIELD_CRATER, FIELD_SIGNAL, FIELD_ROCK,
    FIELD_INFO, DIFFICULTY_SETTINGS,
    GOAL_SIGNAL_RADIUS,
)


class World:
    """
    Reprezentuje dwuwymiarową mapę Marsa.
    Przechowuje specjalne pola jako słownik: {(x, y): typ_pola}.
    Cała reszta to FIELD_NORMAL.
    """

    def __init__(self, difficulty: str, seed: int | None = None) -> None:
        self.difficulty: str = difficulty
        self.seed:       int = seed if seed is not None else random.randint(0, 99999)
        random.seed(self.seed)

        self.fields:    dict[tuple[int, int], str] = {}
        self.goal_pos:  tuple[int, int] = (0, 0)
        self.goal_revealed: bool = False

        # Zapamiętujemy odwiedzone specjalne pola
        self.visited_special: list[tuple[tuple[int, int], str]] = []

        self._generate()

    # ──────────────────────────────────────────────────────────────────────────
    #  GENEROWANIE ŚWIATA
    # ──────────────────────────────────────────────────────────────────────────

    def _generate(self) -> None:
        """Losuje układ pól na mapie."""
        span   = WORLD_MAX - WORLD_MIN       # 100
        area   = span * span                 # 10000 możliwych pól

        # Ilości pól wg trudności
        if self.difficulty == "easy":
            counts = {
                FIELD_DUST:   8,
                FIELD_ICE:    10,
                FIELD_CRATER: 6,
                FIELD_ROCK:   5,
                FIELD_SIGNAL: 3,
            }
        elif self.difficulty == "hard":
            counts = {
                FIELD_DUST:   18,
                FIELD_ICE:    6,
                FIELD_CRATER: 15,
                FIELD_ROCK:   12,
                FIELD_SIGNAL: 3,
            }
        else:   # normal
            counts = {
                FIELD_DUST:   12,
                FIELD_ICE:    8,
                FIELD_CRATER: 10,
                FIELD_ROCK:   8,
                FIELD_SIGNAL: 3,
            }

        occupied: set[tuple[int, int]] = {(0, 0)}   # pozycja startowa zawsze wolna

        for field_type, count in counts.items():
            placed = 0
            attempts = 0
            while placed < count and attempts < count * 50:
                attempts += 1
                x = random.randint(WORLD_MIN, WORLD_MAX)
                y = random.randint(WORLD_MIN, WORLD_MAX)
                if (x, y) not in occupied:
                    self.fields[(x, y)] = field_type
                    occupied.add((x, y))
                    placed += 1

        # Cel misji — daleko od startu, na polu SIGNAL
        self._place_goal(occupied)

    def _place_goal(self, occupied: set[tuple[int, int]]) -> None:
        """Umieszcza główny cel misji (sygnał do przesłania danych)."""
        min_dist = 20   # cel musi być co najmniej 20 pól od startu

        # Zbierz pola SIGNAL i wybierz najdalszy jako główny cel
        signal_fields = [(x, y) for (x, y), t in self.fields.items()
                         if t == FIELD_SIGNAL]

        if signal_fields:
            # Wybierz najdalszy SIGNAL od startu jako cel
            self.goal_pos = max(
                signal_fields,
                key=lambda p: math.sqrt(p[0]**2 + p[1]**2)
            )
        else:
            # Fallback: wygeneruj cel ręcznie
            attempts = 0
            while attempts < 1000:
                attempts += 1
                angle  = random.uniform(0, 2 * math.pi)
                dist   = random.uniform(min_dist, 40)
                gx     = int(round(math.cos(angle) * dist))
                gy     = int(round(math.sin(angle) * dist))
                gx     = max(WORLD_MIN, min(WORLD_MAX, gx))
                gy     = max(WORLD_MIN, min(WORLD_MAX, gy))
                if (gx, gy) not in occupied:
                    self.goal_pos = (gx, gy)
                    self.fields[(gx, gy)] = FIELD_SIGNAL
                    break
            else:
                # Ostateczny fallback
                self.goal_pos = (25, 25)
                self.fields[(25, 25)] = FIELD_SIGNAL

    # ──────────────────────────────────────────────────────────────────────────
    #  ODCZYT POLA
    # ──────────────────────────────────────────────────────────────────────────

    def get_field(self, x: int, y: int) -> str:
        return self.fields.get((x, y), FIELD_NORMAL)

    def get_field_info(self, x: int, y: int) -> dict:
        field = self.get_field(x, y)
        return FIELD_INFO[field]

    def is_passable(self, x: int, y: int) -> bool:
        """Skały są nieprzechodzalne (ruch jest blokowany zawczasu)."""
        return self.get_field(x, y) != FIELD_ROCK

    def is_goal(self, x: int, y: int) -> bool:
        return (x, y) == self.goal_pos

    def distance_to_goal(self, x: int, y: int) -> float:
        gx, gy = self.goal_pos
        return math.sqrt((x - gx)**2 + (y - gy)**2)

    # ──────────────────────────────────────────────────────────────────────────
    #  EFEKTY POLA
    # ──────────────────────────────────────────────────────────────────────────

    def apply_field_effect(
        self,
        x: int,
        y: int,
        rover,         # Rover — unikamy circular import przez type hint string
        difficulty: str,
    ) -> dict | None:
        """
        Stosuje efekt pola pod łazikiem.
        Zwraca słownik z opisem efektu lub None jeśli nic się nie stało.
        """
        field = self.get_field(x, y)
        cfg   = DIFFICULTY_SETTINGS[difficulty]

        if field == FIELD_NORMAL:
            return None

        if field == FIELD_DUST:
            penalty = cfg["dust_penalty"]
            actual  = rover.drain_energy(penalty)
            info = FIELD_INFO[FIELD_DUST]
            return {
                "field":   field,
                "symbol":  info["symbol"],
                "name":    info["name"],
                "desc":    f"Burza pyłowa pochłonęła {actual} jednostek energii!",
                "effect":  f"-{actual} energii",
                "energy_delta": -actual,
            }

        if field == FIELD_ICE:
            bonus  = cfg["ice_bonus"]
            actual = rover.add_energy(bonus)
            info   = FIELD_INFO[FIELD_ICE]
            if actual > 0:
                return {
                    "field":   field,
                    "symbol":  info["symbol"],
                    "name":    info["name"],
                    "desc":    f"Podgrzewacz przetopił lód na wodę i zasilił ogniwa. +{actual} energii.",
                    "effect":  f"+{actual} energii",
                    "energy_delta": actual,
                }
            else:
                return {
                    "field":   field,
                    "symbol":  info["symbol"],
                    "name":    info["name"],
                    "desc":    "Baterie już pełne — lód nie dał dodatkowej energii.",
                    "effect":  "brak efektu (pełna bateria)",
                    "energy_delta": 0,
                }

        if field == FIELD_CRATER:
            penalty = cfg["crater_penalty"]
            info    = FIELD_INFO[FIELD_CRATER]
            # Cofnięcie obsługiwane w simulation.py; tu tylko zwracamy info
            effect_str = f"cofnięcie do poprzedniej pozycji"
            if penalty > 0:
                actual = rover.drain_energy(penalty)
                effect_str += f" oraz -{actual} energii"
            rover.craters_avoided += 1
            return {
                "field":   field,
                "symbol":  info["symbol"],
                "name":    info["name"],
                "desc":    "Krawędź krateru! Łazik musi się cofnąć.",
                "effect":  effect_str,
                "energy_delta": -penalty,
                "pushback": True,
            }

        if field == FIELD_SIGNAL:
            bonus  = cfg["signal_bonus"]
            actual = rover.add_energy(bonus)
            rover.signals_found += 1
            info   = FIELD_INFO[FIELD_SIGNAL]
            # Usuń pole po zebraniu
            if (x, y) in self.fields:
                del self.fields[(x, y)]
            return {
                "field":   field,
                "symbol":  info["symbol"],
                "name":    info["name"],
                "desc":    f"Sygnał zebrany! Dane telemetryczne przesłane do bazy. +{actual} energii.",
                "effect":  f"+{actual} energii, sygnał zebrany",
                "energy_delta": actual,
                "signal_collected": True,
            }

        if field == FIELD_ROCK:
            # Skały nie powinny być osiągalne (blokowane przed ruchem),
            # ale obsługa defensywna
            info = FIELD_INFO[FIELD_ROCK]
            return {
                "field":   field,
                "symbol":  info["symbol"],
                "name":    info["name"],
                "desc":    "Masywna skała blokuje przejście.",
                "effect":  "ruch zablokowany",
                "energy_delta": 0,
                "blocked": True,
            }

        return None

    # ──────────────────────────────────────────────────────────────────────────
    #  PODPOWIEDŹ KIERUNKU DO CELU
    # ──────────────────────────────────────────────────────────────────────────

    def hint_direction(self, from_x: int, from_y: int) -> str:
        """Zwraca przybliżony kierunek do celu misji (jeśli ujawniony)."""
        if not self.goal_revealed:
            return "nieznany"
        gx, gy = self.goal_pos
        dx = gx - from_x
        dy = gy - from_y
        if abs(dx) < 2 and abs(dy) < 2:
            return "bardzo blisko!"
        dirs = []
        if dy > 1:   dirs.append("N")
        if dy < -1:  dirs.append("S")
        if dx > 1:   dirs.append("E")
        if dx < -1:  dirs.append("W")
        return "".join(dirs).lower() if dirs else "?"

    def reveal_goal(self) -> None:
        """Ujawnia lokalizację celu (zdarzenie antena)."""
        self.goal_revealed = True

    # ──────────────────────────────────────────────────────────────────────────
    #  REPREZENTACJA
    # ──────────────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Statystyki mapy."""
        type_counts: dict[str, int] = {}
        for ft in self.fields.values():
            type_counts[ft] = type_counts.get(ft, 0) + 1
        return {
            "seed":      self.seed,
            "goal":      self.goal_pos,
            "fields":    type_counts,
        }