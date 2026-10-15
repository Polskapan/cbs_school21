#!/usr/bin/env python3
import statistics
import sys
import time
from pynput import keyboard

THRESHOLD = 0.1
MAX_ATTEMPTS = 3
MIN_KEYSTROKES = 3


def is_countable(key):
    if key is keyboard.Key.space:
        return True
    return isinstance(key, keyboard.KeyCode) and key.char is not None

"Чтение строки"
def capture(prompt):
    timestamps = []

    def on_press(key):
        if key is keyboard.Key.enter:
            return False  # ввод завершён — останавливаем слушатель
        if is_countable(key):
            timestamps.append(time.perf_counter())

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        text = input(prompt)
    finally:
        listener.stop()
        listener.join()

    return text, intervals(timestamps)


"Подсчёт интервалов"
def intervals(timestamps):
    return [second - first for first, second in zip(timestamps, timestamps[1:])]


"Поиск среднего интервала"
def mean_deviation(first, second):
    length = min(len(first), len(second))
    if length == 0:
        return None
    return statistics.mean(
        abs(a - b) for a, b in zip(first[:length], second[:length])
    )


"Составление описания"
def describe(label, values):
    if not values:
        print(f"{label}: интервалов нет")
        return
    line = (
        f"{label}: нажатий {len(values) + 1}, "
        f"интервалов {len(values)}, "
        f"среднее {statistics.mean(values):.4f} с, "
        f"медиана {statistics.median(values):.4f} с"
    )
    if len(values) > 1:
        line += f", ст. отклонение {statistics.stdev(values):.4f} с"
    print(line)


def main():
    print("Введите строку и нажмите Enter.\n")

    reference, first = capture("Ввод №1: ")

    if len(first) + 1 < MIN_KEYSTROKES:
        sys.exit(
            f"Слишком короткий ввод!!! нужно минимум {MIN_KEYSTROKES} нажатия"
        )

    print("\nВведите ту же самую строку ещё раз\n")

    second = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        repeated, second = capture(f"Ввод №2 (попытка {attempt}): ")
        if repeated == reference:
            break
        print("Строки не совпадают")
    else:
        sys.exit("Строка не была повторена")

    deviation = mean_deviation(first, second)
    if deviation is None:
        sys.exit("Недостаточно данных для сравнения")

    print(f"\nСреднее отклонение: {deviation:.4f} с (порог {THRESHOLD})")

    if deviation > THRESHOLD:
        print("Обнаружены отклонения в поведении. Возможно, вводил другой человек")
    else:
        print("Ввод соответствует исходному пользователю")


if __name__ == "__main__":
    main()
