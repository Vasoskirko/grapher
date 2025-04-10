import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import pandas as pd
from logger import logger

class DataTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Фрейм загрузки данных
        load_frame = ttk.LabelFrame(self, text="Загрузка данных")
        load_frame.pack(fill=BOTH, expand=NO, padx=10, pady=10)

        # Кнопки загрузки
        button_frame = ttk.Frame(load_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text='Загрузить CSV', command=self.controller.load_csv).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text='Загрузить XLSX', command=self.controller.load_xlsx).pack(side=LEFT, padx=5)

        # Таблица предпросмотра
        self.preview_tree = ttk.Treeview(load_frame, show='headings')
        self.preview_tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Информация о данных
        self.info_label = ttk.Label(load_frame, text="")
        self.info_label.pack(pady=5)

        # Основные операции
        self.create_processing_section()

    def create_processing_section(self):
        """Секция обработки данных"""
        processing_frame = ttk.LabelFrame(self, text="Обработка данных")
        processing_frame.pack(fill=BOTH, padx=10, pady=10)

        # Округление данных
        ttk.Button(processing_frame, text='Округлить данные', 
                 command=self.open_rounding_window).grid(row=0, column=0, padx=5)

        # Расчет ячеек
        ttk.Button(processing_frame, text='Рассчитать ячейки', 
                 command=self.calculate_cell_sizes).grid(row=0, column=1, padx=5)

        # Агрегация
        ttk.Button(processing_frame, text='Агрегировать данные', 
                 command=self.open_aggregation_window).grid(row=0, column=2, padx=5)

    # --- Основные методы обработки ---
    def open_rounding_window(self):
        if self.controller.data_frame is None:
            messagebox.showwarning('Ошибка', 'Сначала загрузите данные!')
            return

        window = tk.Toplevel(self)
        window.title('Округление данных')

        # --- Создание элементов интерфейса ---
        columns_frame = ttk.LabelFrame(window, text="Выберите колонки")
        columns_frame.pack(padx=10, pady=10)

        rounding_vars = {}
        for col in self.controller.data_frame.columns:
            var = tk.BooleanVar()
            ttk.Checkbutton(columns_frame, text=col, variable=var).pack(anchor=W)
            rounding_vars[col] = var

        ttk.Label(window, text="Знаков после запятой:").pack()
        decimals_entry = ttk.Entry(window)
        decimals_entry.pack()

        # --- Функция apply_rounding с доступом к self ---
        def apply_rounding():
            nonlocal rounding_vars, decimals_entry
            try:
                selected = [col for col, var in rounding_vars.items() if var.get()]
                decimals = int(decimals_entry.get())
                
                if not selected:
                    raise ValueError("Выберите хотя бы одну колонку")
                
                # Убедимся, что X/Y/Z присутствуют в данных
                required_columns = ['X (m)', 'Y (m)', 'Z (m)']
                missing = [col for col in required_columns if col not in self.controller.data_frame.columns]
                if missing:
                    raise ValueError(f"Для сортировки нужны колонки: {', '.join(missing)}")

                # Округление и сортировка
                self.controller.data_frame = self.controller.data_processor.round_columns(
                    self.controller.data_frame, 
                    selected, 
                    decimals
                )
                
                # Обновление интерфейса
                self.update_preview()
                window.destroy()
                messagebox.showinfo("Успех", "Данные округлены и отсортированы!")
                
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
                logger.error(f"Ошибка округления: {str(e)}")
            except Exception as e:
                messagebox.showerror("Ошибка", "Неизвестная ошибка")
                logger.error(f"Критическая ошибка: {str(e)}")

        # --- Кнопка с правильной привязкой команды ---
        ttk.Button(window, text="Применить", command=apply_rounding).pack(pady=10)
    
    def calculate_cell_sizes(self):
        """Запуск фильтрации стенок и расчета ячеек"""
        try:
            # Создаем окно фильтрации и ждем его закрытия
            self.open_wall_filter_window()
            
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))

    def open_aggregation_window(self):
        """Окно агрегации данных"""
        if self.controller.data_frame is None:
            messagebox.showwarning('Ошибка', 'Сначала загрузите данные!')
            return

        window = tk.Toplevel(self)
        window.title('Агрегация данных')

        # Выбор оси
        ttk.Label(window, text="Ось для группировки:").pack()
        axis_var = ttk.StringVar()
        axis_menu = ttk.Combobox(window, textvariable=axis_var, 
                               values=list(self.controller.data_frame.columns))
        axis_menu.pack()

        # Выбор функций
        ttk.Label(window, text="Колонки для усреднения:").pack()
        target_vars = {}
        for col in self.controller.data_frame.columns:
            var = tk.BooleanVar()
            ttk.Checkbutton(window, text=col, variable=var).pack(anchor=W)
            target_vars[col] = var

        def apply_aggregation():
            try:
                axis = axis_var.get()
                targets = [col for col, var in target_vars.items() if var.get()]
                
                if not axis or not targets:
                    raise ValueError("Выберите ось и минимум одну колонку")
                
                result = self.controller.data_processor.aggregate_data(
                    self.controller.data_frame,
                    axis,
                    targets
                )
                
                # Обновляем данные
                self.controller.data_frame = result
                logger.info(f"Агрегация по {axis}: {targets}")
                self.update_preview()
                self.controller.update_plot_tab()
                window.destroy()
                
            except Exception as e:
                logger.error(f"Ошибка агрегации: {str(e)}")
                messagebox.showerror('Ошибка', str(e))

        ttk.Button(window, text="Применить", command=apply_aggregation).pack(pady=10)

    # --- Вспомогательные методы ---
    def update_preview(self):
        """Обновление предпросмотра данных"""
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.preview_tree["columns"] = list(self.controller.data_frame.columns)
        
        # Обновление заголовков
        for col in self.controller.data_frame.columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100)
        
        # Добавление данных
        rows = self.controller.data_frame.head(20).to_numpy().tolist()
        for row in rows:
            self.preview_tree.insert("", tk.END, values=row)
        
        # Обновление информации
        self.info_label['text'] = (
            f"Строк: {len(self.controller.data_frame)}, "
            f"Столбцов: {len(self.controller.data_frame.columns)}"
        )
    
    def open_wall_filter_window(self):
        """Окно фильтрации стенок (модальное)"""
        window = tk.Toplevel(self)
        window.title("Значения на стенках")
        window.grab_set()  # Блокирует взаимодействие с другими окнами
        window.transient(self)  # Делает окно модальным

        # Вопрос о наличии стенок
        has_walls_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(window, text="Есть значения на стенках", variable=has_walls_var).pack(pady=5)

        # Поля для ввода координат стенок
        ttk.Label(window, text="X (через ;):").pack()
        x_entry = ttk.Entry(window)
        x_entry.pack()

        ttk.Label(window, text="Y (через ;):").pack()
        y_entry = ttk.Entry(window)
        y_entry.pack()

        ttk.Label(window, text="Z (через ;):").pack()
        z_entry = ttk.Entry(window)
        z_entry.pack()

        def apply_filter():
            if not has_walls_var.get():
                window.destroy()
                return

            try:
                # Парсинг координат стенок
                walls = {
                    'x': [float(v.strip()) for v in x_entry.get().split(';')],
                    'y': [float(v.strip()) for v in y_entry.get().split(';')],
                    'z': [float(v.strip()) for v in z_entry.get().split(';')]
                }
                
                # Фильтрация данных
                self.controller.data_frame = self.controller.data_processor.filter_wall_values(
                    self.controller.data_frame, walls
                )
                
                # Проверка наличия данных после фильтрации
                if self.controller.data_frame.empty:
                    raise ValueError("Нет данных для расчета после удаления стенок!")
                
                # Расчет размеров ячеек
                self.controller.data_frame = self.controller.data_processor.calculate_cell_sizes(
                    self.controller.data_frame
                )
                
                # Обновление интерфейса
                self.update_preview()
                window.destroy()
                messagebox.showinfo("Успех", "Стенки удалены, размеры ячеек рассчитаны!")
                
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(window, text="Применить", command=apply_filter).pack(pady=10)

        # Ожидаем закрытия окна
        self.wait_window(window)