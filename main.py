from labirinth import Labyrinth
from logic import ArrayProcessor
from logger import log_event

def main(seed=None):
    """Точка входа в программу. Запускает игру в лабиринт."""
    log_event("Game", "=== ПРОГРАММА ЗАПУЩЕНА ===")
    log_event("Game", "=== ЛОГ ЗАПУЩЕН ===")

    # Создаем генератор с seed для воспроизводимости
    processor = ArrayProcessor(size=7, seed=seed)

    # Генерируем карту шумов (49 элементов для 7x7)
    maze_data = processor.generate(49)
    
    # Визуализация карты шумов (для отладки)
    print("=== КАРТА ШУМОВ ===")
    for i in range(7):
        row = []
        for j in range(7):
            idx = i * 7 + j
            value = maze_data[idx]
            row.append(f"{value:+.2f}")
        print(" ".join(row))
    print("==================\n")

    # Создаем лабиринт на основе карты шумов
    game = Labyrinth(size=7, walls_data=maze_data, seed=seed)

    log_event("Game", "Лабиринт инициализирован через карту шумов")

    game.run()

if __name__ == "__main__":
    # Можно запустить с конкретным seed, например: main(42)
    main(42)
