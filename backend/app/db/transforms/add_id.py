#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys


def add_line_numbers(input_file, output_file=None, start_num=1):
    """
    Добавляет порядковый номер в начало каждой строки файла.

    Args:
        input_file (str): путь к входному файлу
        output_file (str): путь к выходному файлу (если None, будет создан автоматически)
        start_num (int): начальный номер (по умолчанию 1)
    """

    # Если выходной файл не указан, создаем имя автоматически
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_numbered{ext}"

    try:
        # Читаем входной файл и обрабатываем строки
        with open(input_file, "r", encoding="utf-8") as f_in:
            lines = f_in.readlines()

        # Записываем в выходной файл с добавленными номерами
        with open(output_file, "w", encoding="utf-8") as f_out:
            for i, line in enumerate(lines, start=start_num):
                # Убираем символы перевода строки для правильного добавления номера
                line = line.rstrip("\n")
                f_out.write(f"{i};{line}\n")

        print(f"✅ Готово! Обработано {len(lines)} строк.")
        print(f"📁 Выходной файл: {output_file}")

    except FileNotFoundError:
        print(f"❌ Ошибка: Файл '{input_file}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при обработке файла: {e}")
        sys.exit(1)


def main():
    """Основная функция для запуска из командной строки."""

    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  python {sys.argv[0]} входной_файл [выходной_файл]")
        print(f"  python {sys.argv[0]} входной_файл --start N")
        print("\nПримеры:")
        print(f"  python {sys.argv[0]} input.txt output.txt")
        print(f"  python {sys.argv[0]} data.csv --start 100")
        sys.exit(1)

    # Парсим аргументы
    input_file = sys.argv[1]
    output_file = None
    start_num = 1

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--start" and i + 1 < len(sys.argv):
            try:
                start_num = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("❌ Ошибка: Начальный номер должен быть целым числом.")
                sys.exit(1)
        else:
            output_file = sys.argv[i]
            i += 1

    # Вызываем основную функцию
    add_line_numbers(input_file, output_file, start_num)


if __name__ == "__main__":
    main()
