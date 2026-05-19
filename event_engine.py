"""
events.py — Silnik zdarzeń losowych
=====================================
Losuje i stosuje zdarzenia które mogą wystąpić w każdym kroku.
"""

from __future__ import annotations
import random
from config import EVENTS, DIFFICULTY_SETTINGS


class EventEngine:
    """Zarządza zdarzeniami losowymi podczas wyprawy."""

    def __init__(self, difficulty: str) -> None:
        self.difficulty: str   = difficulty
        self.chance:     float = DIFFICULTY_SETTINGS[difficulty]["event_chance"]
        self.log:        list[dict] = []   # wszystkie zdarzenia z całej gry

    # ──────────────────────────────────────────────────────────────────────────

    def roll(self, step: int) -> dict | None:
        """
        Losuje zdarzenie dla danego kroku.
        Zwraca słownik zdarzenia lub None jeśli nic się nie wydarzyło.
        """
        if random.random() > self.chance:
            return None

        event = random.choice(EVENTS).copy()
        event["step"] = step

        # Losuj magnitudę dla zdarzeń energetycznych (±20% wartości bazowej)
        if event["effect"] == "energy" and event["value"] != 0:
            base = event["value"]
            variation = int(abs(base) * 0.2)
            if base > 0:
                event["value"] = base + random.randint(-variation, variation)
            else:
                event["value"] = base - random.randint(-variation, variation)

        return event

    def apply(self, event: dict, rover, world) -> str:
        """
        Stosuje efekt zdarzenia do łazika/świata.
        Zwraca opis efektu dla wyświetlenia w terminalu.
        rover: Rover
        world: World
        """
        effect = event["effect"]
        value  = event["value"]
        desc   = event["desc"]

        if effect == "energy":
            if value > 0:
                actual = rover.add_energy(value)
                result = f"+{actual} energii"
            else:
                actual = rover.drain_energy(abs(value))
                result = f"-{actual} energii"
            rover.events_survived += 1
            event["applied_result"] = result
            self.log.append(event)
            return result

        if effect == "pushback":
            # Cofnięcie do losowej sąsiedniej pozycji z oryginalnej
            from config import WORLD_MIN, WORLD_MAX
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            old_x, old_y = rover.x, rover.y
            rover.force_move(dx, dy)
            result = f"cofnięcie do ({rover.x}, {rover.y})"
            rover.events_survived += 1
            event["applied_result"] = result
            self.log.append(event)
            return result

        if effect == "reveal_goal":
            world.reveal_goal()
            hint = world.hint_direction(rover.x, rover.y)
            result = f"Cel misji ujawniony! Kierunek: {hint}"
            rover.events_survived += 1
            event["applied_result"] = result
            self.log.append(event)
            return result

        if effect == "random_move":
            directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
            dx, dy = random.choice(directions)
            rover.force_move(dx, dy)
            result = f"łazik przesunięty do ({rover.x}, {rover.y})"
            rover.events_survived += 1
            event["applied_result"] = result
            self.log.append(event)
            return result

        # Nieznany efekt — bezpieczny fallback
        event["applied_result"] = "bez efektu"
        self.log.append(event)
        return "bez efektu"

    def summary(self) -> list[dict]:
        """Zwraca listę wszystkich zdarzeń z gry."""
        return self.log