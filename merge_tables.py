import pandas as pd
import tkinter as tk
from tkinter import filedialog
import csv

# Скрываем главное окно Tkinter
root = tk.Tk()
root.withdraw()

# Запрос выбора CSV файлов (несколько файлов можно выбрать)
file_paths = filedialog.askopenfilenames(
    title="Выберите CSV файлы",
    filetypes=[("CSV файлы", "*.csv")]
)

if not file_paths:
    print("Файлы не выбраны!")
    exit()

# Читаем каждый выбранный файл в DataFrame
dataframes = []
for path in file_paths:
    try:
        df = pd.read_csv(path)
        dataframes.append(df)
    except Exception as e:
        print(f"Ошибка при чтении файла {path}: {e}")

if not dataframes:
    print("Нет корректных файлов для обработки!")
    exit()

# Объединяем таблицы столбец за столбцом.
# Используем innerjoin (или объединяем с outer и затем dropna), чтобы удалить строки с пустыми ячейками,
# появляющимися из-за различного количества строк.
merged_df = pd.concat(dataframes, axis=1, join='inner')

# Удаляем строки, где имеется хотя бы одна пустая ячейка
merged_df.dropna(axis=0, how='any', inplace=True)

# Сохраняем итоговую таблицу в новый CSV файл.
# Параметр quoting=csv.QUOTE_ALL заставит взять в кавычки все поля, в том числе и названия колонок.
output_file = filedialog.asksaveasfilename(
    title="Сохранить объединённый CSV",
    defaultextension=".csv",
    filetypes=[("CSV файлы", "*.csv")]
)

if output_file:
    merged_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
    print(f"Файл успешно сохранён: {output_file}")
else:
    print("Сохранение отменено.")
