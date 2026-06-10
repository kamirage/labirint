import collections
import random

from logger import log_event


class Labyrinth:
    """
    Класс, управляющий игрой в лабиринте.
    Содержит поле, игрока, врага и логику преследования.
    """

    def __init__(self, size=7, walls_data=None, seed=None):
        self.size = size
        self.wall = "#"
        self.road = "."
        self.player = "P"
        self.enemy = "E"

        self.p_pos = [1, 1]
        self.e_pos = [size - 2, size - 2]

        self.seed = seed
        if seed is not None:
            random.seed(seed)
            log_event("Maze", f"Установлен seed: {seed}")

        self.grid = self._generate_valid_maze(walls_data)

        log_event("Maze", f"Создан лабиринт размером {size}x{size}")
        log_event("Player", f"Создан игрок на позиции ({self.p_pos[0]}, {self.p_pos[1]})")
        log_event("Enemy", f"Создан враг на позиции ({self.e_pos[0]}, {self.e_pos[1]})")

    def _generate_valid_maze(self, walls_data=None):
        """
        Генерирует лабиринт.
        """
        grid = [[self.road for _ in range(self.size)] for _ in range(self.size)]

        for i in range(self.size):
            grid[0][i] = self.wall
            grid[self.size - 1][i] = self.wall
            grid[i][0] = self.wall
            grid[i][self.size - 1] = self.wall

        walls_count = 0
        if walls_data:
            walls_count = self._add_walls_from_data(grid, walls_data)

            if not self._has_path(grid, self.p_pos, self.e_pos):
                log_event("Maze", "Сгенерированный лабиринт непроходим! Создаём альтернативный...")
                grid = self._create_safe_maze()
                walls_count = self._count_walls(grid)
            else:
                log_event("Maze", f"Построено {walls_count} стен, путь существует")
        else:
            grid = self._create_safe_maze()
            walls_count = self._count_walls(grid)
            log_event("Maze", f"Создан безопасный лабиринт с {walls_count} стенами")

        return grid

    def _add_walls_from_data(self, grid, data):
        """Добавляет стены на основе данных массива."""
        walls_count = 0
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                if [i, j] == self.p_pos or [i, j] == self.e_pos:
                    continue
                idx = (i - 1) * (self.size - 2) + (j - 1)
                if idx < len(data) and data[idx] > 50:
                    grid[i][j] = self.wall
                    walls_count += 1
        return walls_count

    def _has_path(self, grid, start, target):
        """Проверяет, существует ли путь от start до target."""
        queue = collections.deque([tuple(start)])
        seen = {tuple(start)}

        while queue:
            curr = queue.popleft()
            if list(curr) == target:
                return True

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = curr[0] + dx, curr[1] + dy
                if (0 <= nx < self.size and 0 <= ny < self.size
                        and grid[nx][ny] != self.wall
                        and (nx, ny) not in seen):
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        return False

    def _create_safe_maze(self):
        """
        Создаёт гарантированно проходимый лабиринт:
        """
        grid = [[self.road for _ in range(self.size)] for _ in range(self.size)]

        for i in range(self.size):
            grid[0][i] = self.wall
            grid[self.size - 1][i] = self.wall
            grid[i][0] = self.wall
            grid[i][self.size - 1] = self.wall

        attempts = 0
        while attempts < 30:
            test_grid = [row[:] for row in grid]

            new_walls = 0
            for _ in range(5):
                i = random.randint(1, self.size - 2)
                j = random.randint(1, self.size - 2)
                if [i, j] != self.p_pos and [i, j] != self.e_pos and test_grid[i][j] != self.wall:
                    test_grid[i][j] = self.wall
                    new_walls += 1

            if self._has_path(test_grid, self.p_pos, self.e_pos):
                grid = test_grid
                log_event("Maze", f"Добавлено {new_walls} случайных стен, путь сохранился")
                break

            attempts += 1

        return grid

    def _count_walls(self, grid):
        """Подсчитывает количество стен в лабиринте."""
        return sum(row.count(self.wall) for row in grid)

    def _get_next_step(self, start, target):
        """
        Возвращает следующий шаг от start к target по кратчайшему пути.
        Используется врагом для преследования игрока.
        """
        queue = collections.deque([[start]])
        seen = {tuple(start)}

        while queue:
            path = queue.popleft()
            curr = path[-1]

            if curr == target:
                return path[1] if len(path) > 1 else start

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nxt = [curr[0] + dx, curr[1] + dy]
                if 0 <= nxt[0] < self.size and 0 <= nxt[1] < self.size \
                        and self.grid[nxt[0]][nxt[1]] != self.wall \
                        and tuple(nxt) not in seen:
                    seen.add(tuple(nxt))
                    queue.append(path + [nxt])
        return start

    def display(self):
        """Выводит текущее состояние лабиринта в консоль."""
        print("\n" + "-" * (self.size * 2 + 4))
        for r in range(self.size):
            row = []
            for c in range(self.size):
                if [r, c] == self.p_pos:
                    row.append(self.player)
                elif [r, c] == self.e_pos:
                    row.append(self.enemy)
                else:
                    row.append(self.grid[r][c])
            print(" | " + " ".join(row) + " | ")
        print("-" * (self.size * 2 + 4))

    def move_player(self, direction):
        """
        Перемещает игрока, если новая клетка не является стеной.
        direction: 'w', 's', 'a', 'd'
        """
        d_map = {'w': [-1, 0], 's': [1, 0], 'a': [0, -1], 'd': [0, 1]}
        d = d_map.get(direction, [0, 0])
        new_p = [self.p_pos[0] + d[0], self.p_pos[1] + d[1]]

        if 0 <= new_p[0] < self.size and 0 <= new_p[1] < self.size \
                and self.grid[new_p[0]][new_p[1]] != self.wall:
            old_pos = tuple(self.p_pos)
            self.p_pos = new_p
            log_event("Player", f"Переместился с {old_pos} на ({self.p_pos[0]}, {self.p_pos[1]})")
            return True
        else:
            log_event("Player", f"Стена - движение невозможно в направлении {direction}")
            return False

    def move_enemy(self):
        """Движение врага"""
        old_pos = tuple(self.e_pos)
        self.e_pos = list(self._get_next_step(self.e_pos, self.p_pos))
        log_event("Enemy", f"Переместился с {old_pos} на ({self.e_pos[0]}, {self.e_pos[1]})")

    def is_caught(self):
        """Проверка, съел ли враг игрока."""
        caught = self.p_pos == self.e_pos
        if caught:
            print("Тебя съели!")
            log_event("Game", "Враг поймал игрока!")
        return caught

    def run(self):
        """Главный игровой цикл."""
        log_event("Game", "=== ИГРА ЗАПУЩЕНА ===")

        while True:
            self.display()

            if self.is_caught():
                break

            move = input("WASD: ").lower()
            if move not in ['w', 's', 'a', 'd']:
                print("Неверная клавиша! Используйте W, A, S, D")
                continue

            self.move_player(move)
            self.move_enemy()

        log_event("Game", "=== ИГРА ЗАВЕРШЕНА ===")