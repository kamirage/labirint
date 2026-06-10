import math
import random
from logger import file_logger, log_event

class NoiseGenerator:
    """
    Генератор карт шумов (Simplex/Perlin-like noise).
    Создает 2D массив значений от -1 до 1.
    """
    
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randint(0, 10000)
        random.seed(self.seed)
        
        # Генерируем перестановки для шума
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm *= 2  # Дублируем для избежания индексации
        
        log_event("NoiseGenerator", f"Инициализирован генератор шума с seed={self.seed}")
    
    def _fade(self, t):
        """Функция сглаживания (6t^5 - 15t^4 + 10t^3)"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, t, a, b):
        """Линейная интерполяция"""
        return a + t * (b - a)
    
    def _grad(self, hash, x, y):
        """Вычисляет градиент"""
        h = hash & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise_2d(self, x, y):
        """
        Генерирует значение шума Перлина для координат (x, y).
        Возвращает значение от -1 до 1.
        """
        # Находим целые координаты ячейки
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        
        # Относительные координаты внутри ячейки
        x -= math.floor(x)
        y -= math.floor(y)
        
        # Функции сглаживания
        u = self._fade(x)
        v = self._fade(y)
        
        # Хэши углов
        A = self.perm[X] + Y
        AA = self.perm[A]
        AB = self.perm[A + 1]
        B = self.perm[X + 1] + Y
        BA = self.perm[B]
        BB = self.perm[B + 1]
        
        # Интерполяция градиентов
        return self._lerp(v,
            self._lerp(u, self._grad(self.perm[AA], x, y),
                          self._grad(self.perm[BA], x - 1, y)),
            self._lerp(u, self._grad(self.perm[AB], x, y - 1),
                          self._grad(self.perm[BB], x - 1, y - 1))
        )
    
    def generate_noise_map(self, width, height, scale=0.1, octaves=1, persistence=0.5, lacunarity=2.0):
        """
        Генерирует 2D карту шумов.
        
        Args:
            width, height: размеры карты
            scale: масштаб шума (чем меньше, тем крупнее "рябь")
            octaves: количество октав (слоев шума для детализации)
            persistence: затухание каждой октавы
            lacunarity: увеличение частоты для каждой октавы
            
        Returns:
            2D массив значений от -1 до 1
        """
        noise_map = []
        
        for y in range(height):
            row = []
            for x in range(width):
                noise_value = 0
                frequency = scale
                amplitude = 1.0
                max_amplitude = 0.0
                
                # Наложение октав (Fractal Brownian Motion)
                for _ in range(octaves):
                    sample_x = x * frequency
                    sample_y = y * frequency
                    
                    noise_value += self.noise_2d(sample_x, sample_y) * amplitude
                    
                    max_amplitude += amplitude
                    amplitude *= persistence
                    frequency *= lacunarity
                
                # Нормализация в диапазон [-1, 1]
                noise_value /= max_amplitude
                row.append(noise_value)
            
            noise_map.append(row)
        
        log_event("NoiseGenerator", f"Сгенерирована карта шумов {width}x{height}")
        return noise_map


class ArrayProcessor:
    """
    Класс для работы с картами шумов вместо случайных чисел.
    """

    def __init__(self, size=10, seed=None):
        self._size = size
        self.seed = seed
        self.noise_gen = NoiseGenerator(seed)
        log_event("ArrayProcessor", f"Создан экземпляр класса с размером {size}")

    def generate(self, count):
        """
        Генерирует карту шумов и возвращает как одномерный массив.
        count - общее количество элементов (должен быть квадратом размера).
        """
        # Вычисляем размер стороны (предполагаем квадрат)
        side_size = int(math.sqrt(count))
        if side_size * side_size != count:
            # Если не квадрат, берем ближайший
            side_size = int(math.ceil(math.sqrt(count)))
            count = side_size * side_size
        
        # Генерируем 2D карту шумов
        noise_map = self.noise_gen.generate_noise_map(
            width=side_size,
            height=side_size,
            scale=0.15,  # Масштаб "ряби"
            octaves=3,   # 3 слоя для детализации
            persistence=0.5,
            lacunarity=2.0
        )
        
        # Преобразуем в одномерный массив
        result = []
        for row in noise_map:
            result.extend(row)
        
        log_event("Game", f"Сгенерирована карта шумов из {len(result)} элементов")
        return result

    def generate_noise_map_2d(self, width, height):
        """
        Генерирует и возвращает 2D карту шумов напрямую.
        """
        return self.noise_gen.generate_noise_map(
            width=width,
            height=height,
            scale=0.15,
            octaves=3,
            persistence=0.5,
            lacunarity=2.0
        )

    @file_logger
    def multiply_elements(self, factor):
        """Умножает каждый элемент массива на factor."""
        self._data = [x * factor for x in self._data]
        return self._data

    @file_logger
    def half_to_zeros(self):
        """Заменяет первую половину массива нулями."""
        mid = (len(self._data) + 1) // 2
        self._data[:mid] = [0] * mid
        return self._data

    @file_logger
    def get_current_array(self):
        """Возвращает текущее состояние массива."""
        return self._data
