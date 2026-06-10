import functools
from datetime import datetime


def log_event(event_type, message):
    """
    Записывает событие в log.txt.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{event_type}] {message}\n")


def file_logger(func):
    """
    Декоратор для логирования результата в файл log.txt.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_str = f"({', '.join(repr(a) for a in args[1:])})"
        kwargs_str = f", {kwargs}" if kwargs else ""
        log_event("Decorator", f"Вызов метода {func.__name__} с аргументами: {args_str}{kwargs_str}")

        result = func(*args, **kwargs)

        log_event("Decorator", f"Метод {func.__name__} вернул: {result}")

        return result

    return wrapper