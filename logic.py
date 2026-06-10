import random
from logger import file_logger, log_event

class ArrayProcessor:
    """
    Класс для работы с одномерным массивом.
    """

    def __init__(self, size=10):
        self._size = size
        self._data = [random.randint(1, 100) for _ in range(size)]
        log_event("ArrayProcessor", f"Создан экземпляр класса с размером {size}")

    def generate(self, count):
        """Генерирует массив случайных чисел заданного размера."""
        result = [round(random.uniform(1, 100), 2) for _ in range(count)]
        log_event("Game", f"Сгенерирован массив из {count} элементов")
        return result

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