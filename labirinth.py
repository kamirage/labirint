import collections
import random
import math

from logger import log_event

class Labyrinth:
    """
    Класс, управляющий игрой в лабиринте.
    Использует карты шумов для процедурной генерации.
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
        Генерирует лабиринт на основе карты шумов.
        """
        grid = [[self.road for _ in range(self.size)] for _ in range(self.size)]

        # Создаем границы (стены по краям)
        for i in range(self.size):
            grid[0][i] = self.wall
            grid[self.size - 1][i] = self.wall
            grid[i][0] = self.wall
            grid[i][self.size - 1] = self.wall

        walls_count = 0
        if walls_data:
            walls_count = self._add_walls_from_noise(grid, walls_data)

        # Проверяем проходимость
        if not self._has_path(grid, self.p_pos, self.e_pos):
            log_event("Maze", "Сгенерированный лабиринт непроходим! Создаём альтернативный...")
            grid = self._create_safe_maze()
            walls_count = self._count_walls(grid)
        else:
            log_event("Maze", f"Построено {walls_count} стен из карты шумов, путь существует")

        return grid

    def _add_walls_from_noise(self, grid, noise_data):
        """
        Добавляет стены на основе карты шумов.
        Темная зона (-1) = стена, светлая зона (1) = дорога.
        Порог: если значение > 0, то дорога, иначе стена.
        """
        walls_count = 0
        side_size = int(math.sqrt(len(noise_data)))
        
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                # Пропускаем позиции игрока и врага
                if [i, j] == self.p_pos or [i, j] == self.e_pos:
                    continue
                
                # Вычисляем индекс в одномерном массиве шумов
                idx = (i - 1) * (self.size - 2) + (j - 1)
                
                if idx < len(noise_data):
                    noise_value = noise_data[idx]
                    
                    # Логика: темная зона (-1) = стена, светлая (1) = дорога
                    # Порог 0: если значение < 0, то стена
                    # Можно настроить порог (например, -0.2 для большего количества дорог)
                    threshold = 0.0
                    
                    if noise_value < threshold:
                        grid[i][j] = self.wall
                        walls_count += 1
                        log_event("Maze", f"Стена на ({i},{j}): шум={noise_value:.2f} < {threshold}")
                    else:
                        grid[i][j] = self.road
        
        return walls_count

    def _create_safe_maze(self):
        """
        Создаёт гарантированно проходимый лабиринт (fallback).
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

    def _has_path(self, grid, start, end):
        """Проверяет существование пути от start до end (BFS)."""
        visited = set()
        queue = collections.deque([tuple(start)])
        visited.add(tuple(start))

        while queue:
            current = queue.popleft()
            
            if list(current) == end:
                return True

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current[0] + dx, current[1] + dy
                
                if (0 <= nx < self.size and 0 <= ny < self.size and 
                    grid[nx][ny] != self.wall and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False

    def _count_walls(self, grid):
        """Считает количество стен."""
        count = 0
        for row in grid:
            for cell in row:
                if cell == self.wall:
                    count += 1
        return count

    def display(self):
        """Отображает лабиринт."""
        for i in range(self.size):
            row_str = ""
            for j in range(self.size):
                if [i, j] == self.p_pos:
                    row_str += self.player + " "
                elif [i, j] == self.e_pos:
                    row_str += self.enemy + " "
                else:
                    row_str += self.grid[i][j] + " "
            print(row_str)
        print()

    def move_player(self, direction):
        """Перемещает игрока."""
        dx, dy = 0, 0
        if direction == 'w': dx = -1
        elif direction == 's': dx = 1
        elif direction == 'a': dy = -1
        elif direction == 'd': dy = 1

        new_pos = [self.p_pos[0] + dx, self.p_pos[1] + dy]
        
        if (0 <= new_pos[0] < self.size and 0 <= new_pos[1] < self.size and 
            self.grid[new_pos[0]][new_pos[1]] != self.wall):
            self.p_pos = new_pos
            log_event("Player", f"Игрок переместился на ({self.p_pos[0]}, {self.p_pos[1]})")

    def move_enemy(self):
        """Перемещает врага к игроку (простой AI)."""
        dx = 0 if self.e_pos[0] == self.p_pos[0] else (1 if self.p_pos[0] > self.e_pos[0] else -1)
        dy = 0 if self.e_pos[1] == self.p_pos[1] else (1 if self.p_pos[1] > self.e_pos[1] else -1)

        # Пытаемся двигаться по X
        new_pos = [self.e_pos[0] + dx, self.e_pos[1]]
        if (0 <= new_pos[0] < self.size and 0 <= new_pos[1] < self.size and 
            self.grid[new_pos[0]][new_pos[1]] != self.wall):
            self.e_pos = new_pos
        else:
            # Пытаемся двигаться по Y
            new_pos = [self.e_pos[0], self.e_pos[1] + dy]
            if (0 <= new_pos[0] < self.size and 0 <= new_pos[1] < self.size and 
                self.grid[new_pos[0]][new_pos[1]] != self.wall):
                self.e_pos = new_pos

    def is_caught(self):
        """Проверяет, пойман ли игрок."""
        return self.p_pos == self.e_pos

    def run(self):
        """Главный игровой цикл."""
        log_event("Game", "=== ИГРА ЗАПУЩЕНА ===")

        while True:
            self.display()

            if self.is_caught():
                print("Вас поймали!")
                break

            move = input("WASD: ").lower()
            if move not in ['w', 's', 'a', 'd']:
                print("Неверная клавиша! Используйте W, A, S, D")
                continue

            self.move_player(move)
            self.move_enemy()

        log_event("Game", "=== ИГРА ЗАВЕРШЕНА ===")
