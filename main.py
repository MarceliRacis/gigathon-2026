"""
main.py — Punkt wejścia symulacji łazika ARES
==============================================
Uruchom ten plik, aby rozpocząć symulację:

    python main.py

Wymagania: Python 3.11+ | Brak zewnętrznych zależności.
"""

import sys
import lib as L
import display as D
import setup as S
from simulation import Simulation


def main() -> None:
    """Główna pętla programu z możliwością ponownego uruchomienia."""

    # Ekran powitalny (raz na sesję)
    D.splash_screen()
    D.mission_briefing()

    play_again = True
    session_scores: list[tuple[str, int, str]] = []   # (nazwa, wynik, wynik_label)

    while play_again:
        # ── Konfiguracja misji ────────────────────────────────────────────────
        rover, world, engine, max_steps = S.gather_parameters()

        # ── Symulacja ─────────────────────────────────────────────────────────
        sim    = Simulation(rover, world, engine, max_steps)
        report = sim.run()

        # ── Ekran końca i raport ──────────────────────────────────────────────
        D.show_end_screen(report["outcome"])
        L.pause(0.8)
        D.show_report(report)

        session_scores.append((
            report["rover_name"],
            report["score"],
            report["outcome_label"],
        ))

        # ── Tablica wyników sesji (jeśli >1 gra) ─────────────────────────────
        if len(session_scores) > 1:
            _show_session_leaderboard(session_scores)

        # ── Pytanie o ponowne uruchomienie ────────────────────────────────────
        print()
        again = L.prompt_choice(
            "Rozpocząć nową misję?",
            choices=["tak", "nie"],
        )
        play_again = (again == "tak")
        print()

    # ── Pożegnanie ────────────────────────────────────────────────────────────
    L.separator("═", L.bright_red)
    print(L.bold_cyan("  Dziękujemy za udział w programie ARES-MISSION.".center(L.terminal_width())))
    print(L.dim("  Misja zakończona. Do zobaczenia na Marsie.".center(L.terminal_width())))
    L.separator("═", L.bright_red)
    print()
    sys.exit(0)


def _show_session_leaderboard(scores: list[tuple[str, int, str]]) -> None:
    """Wyświetla tabelę wyników z bieżącej sesji."""
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    lines = []
    for i, (name, score, label) in enumerate(sorted_scores, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"  {i}."
        col   = L.bright_green if i == 1 else (L.bright_yellow if i == 2 else L.bright_cyan)
        lines.append(
            f"  {medal}  {col(name):<20}  {L.bold_white(str(score)+' pkt'):<12}  {L.dim(label)}"
        )
    L.box("TABELA WYNIKÓW SESJI", lines, color_fn=L.bright_yellow, title_fn=L.bold_yellow)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(L.warn("  Przerwano przez użytkownika (Ctrl+C)."))
        print(L.dim("  Misja anulowana."))
        print()
        sys.exit(0)