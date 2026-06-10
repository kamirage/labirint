from labirinth import Labyrinth
from logic import ArrayProcessor
from logger import log_event


def main(seed=None):
    """Точка входа в программу. Запускает игру в лабиринт."""
    log_event("Game", "=== ПРОГРАММА ЗАПУЩЕНА ===")
    log_event("Game", "=== ЛОГ ЗАПУЩЕН ===")

    processor = ArrayProcessor(size=10)

    maze_data = processor.generate(49)

    game = Labyrinth(size=7, walls_data=maze_data, seed=seed)

    log_event("Game", "Лабиринт инициализирован через логический модуль")

    game.run()


if __name__ == "__main__":
    # Можно запустить с конкретным seed, например: main(42)
    main(42)