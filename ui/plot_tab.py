import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tkinter import messagebox
from logger import logger
import pandas as pd
from preview_window import PreviewWindow


class PlotTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.curves = controller.curves
        self.style_var = controller.style_var
        self.show_right_axis = controller.show_right_axis
        self.xlabel_var = controller.xlabel_var
        self.ylabel_var = controller.ylabel_var
        self.title_var = controller.title_var
        self.x_menu = None
        self.y_menu = None
        self.create_widgets()
        
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Entry):
                self.enable_copy_paste(widget)
        
    def create_widgets(self):
        self.create_graph_settings()
        self.create_curve_settings()
        self.create_theoretical_data_section()
        self.create_curve_list()
        self.create_plot_buttons()

    def show_theory_preview(self):
        """Показ превью аналогично основным данным"""
        if self.controller.theory_data is not None:
            PreviewWindow(self, self.controller.theory_data)

    def create_theoretical_data_section(self):
        # Создаем фрейм для теоретических данных
        theory_frame = ttk.LabelFrame(self, text="Теоретические данные")
        theory_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # Кнопка для загрузки теоретических данных
        ttk.Button(theory_frame, text='Загрузить теорию (CSV)',
                 command=self.controller.load_theoretical_data).grid(row=0, column=0)
        
        # Информация о загруженных теоретических данных
        self.theory_info = ttk.Label(theory_frame, text="Данные не загружены")
        self.theory_info.grid(row=0, column=1)

        self.theory_preview = ttk.Button(theory_frame, text='Просмотр', 
                                       command=self.show_theory_preview)
        self.theory_preview.grid(row=1, column=0)

        # Кнопка для добавления теоретических данных на график
        ttk.Button(theory_frame, text='Добавить на график',
                   command=self.add_theoretical_curve).grid(
            row=1, column=0, padx=5, pady=5, sticky='w')
        

    def add_theoretical_curve(self):
        try:
            if self.controller.theory_data is None:
                messagebox.showwarning('Предупреждение', 'Сначала загрузите теоретические данные')
                return

            column_window = ttk.Toplevel(self)
            column_window.title('Выбор данных для осей')
            
            # Получаем актуальные названия колонок
            columns = self.controller.theory_data.columns.tolist()
            
            # Выбор осей
            ttk.Label(column_window, text="Ось X:").grid(row=0, column=0)
            x_var = ttk.StringVar(value=columns[0] if columns else '')
            x_combobox = ttk.Combobox(column_window, textvariable=x_var, values=columns)
            x_combobox.grid(row=0, column=1)

            ttk.Label(column_window, text="Ось Y:").grid(row=1, column=0)
            y_var = ttk.StringVar(value=columns[1])
            y_combobox = ttk.Combobox(column_window, textvariable=y_var, values=columns)
            y_combobox.grid(row=1, column=1)

            # Настройки отображения
            ttk.Label(column_window, text="Цвет кривой:").grid(row=2, column=0)
            color_var = ttk.StringVar(value='red')
            ttk.Combobox(column_window, textvariable=color_var,
                        values=['red', 'blue', 'green', 'black']).grid(row=2, column=1)

            ttk.Label(column_window, text="Вид кривой:").grid(row=3, column=0)
            style_var = ttk.StringVar(value='--')
            ttk.Combobox(column_window, textvariable=style_var,
                        values=['-', '--', '-.', ':']).grid(row=3, column=1)

            ttk.Label(column_window, text="Подпись:").grid(row=4, column=0)
            label_var = ttk.StringVar(value='Теория')
            ttk.Entry(column_window, textvariable=label_var).grid(row=4, column=1)

            def add_curve():
                try:
                    # Проверка существования колонок
                    x_col = x_var.get()
                    y_col = y_var.get()
                    
                    if x_col not in columns:
                        raise ValueError(f"Колонка X '{x_col}' не найдена")
                    if y_col not in columns:
                        raise ValueError(f"Колонка Y '{y_col}' не найдена")
                    
                    # Безопасное получение данных
                    x_data = self.controller.theory_data[x_col].values
                    y_data = self.controller.theory_data[y_col].values

                    new_curve = {
                        'x': x_data,
                        'y': y_data,
                        'color': color_var.get(),
                        'style': style_var.get(),
                        'label': label_var.get(),
                        'is_theory': True,
                        'axis': 'left'
                    }
                    self.controller.theory_curves.append(new_curve)
                    self.controller.plot_tab.update_curve_list()
                    column_window.destroy()
                    messagebox.showinfo('Успех', 'Кривая добавлена')
                except Exception as e:
                    messagebox.showerror('Ошибка', f'Ошибка: {str(e)}')
                    logger.error(f"Ошибка добавления кривой: {str(e)}")

            ttk.Button(column_window, text="Добавить", command=add_curve).grid(row=5, columnspan=2)
            
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка: {str(e)}')
            logger.error(f"Ошибка добавления теоретической кривой: {str(e)}")


    def create_curve_settings(self):
        self.curve_frame = ttk.LabelFrame(self, text="Настройки кривой")
        self.curve_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # Первая колонка
        first_column = [
            ('Ось X:', self.controller.x_var, None),
            ('Ось Y:', self.controller.y_var, None),
            ('Имя легенды:', self.controller.curve_label_var, None),
            ('Положение оси:', self.controller.axis_var, ['left', 'right']),
            ('Использовать маркеры', self.controller.show_marker_var, ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*']),
            ('Стиль линии:', self.controller.line_style_var, ['-', '--', '-.', ':']),
            ('Цвет линии:', self.controller.color_var, ['blue', 'red', 'green', 'orange', 'purple']),
            ('Толщина линии:', self.controller.line_width_var, None),
            ('Расположение легенды:', self.controller.legend_position_var, ['upper right', 'upper left', 'lower left', 'lower right'])
        ]

        for i, (label, var, values) in enumerate(first_column):
            if label == 'Использовать маркеры':
                frame = ttk.Frame(self.curve_frame)
                frame.grid(row=i, column=0, columnspan=2, padx=5, pady=2, sticky='w')
                
                cb = ttk.Checkbutton(
                    frame,
                    text=label,
                    variable=var,
                    command=self.update_marker_style_state
                )
                cb.pack(side='left')
                
                self.marker_style_combobox = ttk.Combobox(
                    frame,
                    textvariable=self.controller.marker_var,
                    values=values,
                    state='disabled',
                    width=3
                )
                self.marker_style_combobox.pack(side='left', padx=5)
                continue

            if label in ('Ось X:', 'Ось Y:'):
                ttk.Label(self.curve_frame, text=label, width=12).grid(row=i, column=0, padx=5, pady=2, sticky='w')
                combobox = ttk.Combobox(
                    self.curve_frame,
                    textvariable=var,
                    values=[],
                    width=18
                )
                combobox.grid(row=i, column=1, padx=5, pady=2, sticky='w')
                
                if label == 'Ось X:':
                    self.x_menu = combobox
                elif label == 'Ось Y:':
                    self.y_menu = combobox

                continue

            if isinstance(var, tk.BooleanVar):
                ttk.Checkbutton(
                    self.curve_frame,
                    text=label,
                    variable=var
                ).grid(row=i, column=0, padx=5, pady=2, sticky='w')
            else:
                ttk.Label(self.curve_frame, text=label, width=14).grid(row=i, column=0, padx=5, pady=2, sticky='w')
                
                if values:
                    ttk.Combobox(
                        self.curve_frame,
                        textvariable=var,
                        values=values,
                        width=12
                    ).grid(row=i, column=1, padx=5, pady=2, sticky='w')
                else:
                    ttk.Entry(
                        self.curve_frame,
                        textvariable=var,
                        width=10
                    ).grid(row=i, column=1, padx=5, pady=2, sticky='w')

        # Вторая колонка: Масштабы
        second_column = [
            ('Масштаб X:', self.controller.x_scale_var, ['linear', 'log']),
            ('Масштаб Y:', self.controller.y_scale_var, ['linear', 'log'])
        ]
        for i, (label, var, values) in enumerate(second_column):
            ttk.Label(self.curve_frame, text=label).grid(row=i, column=2, padx=5, pady=2, sticky='w')
            ttk.Combobox(
                self.curve_frame,
                textvariable=var,
                values=values,
                width=10
            ).grid(row=i, column=3, padx=5, pady=2, sticky='w')

        # Третья колонка: Минимальные значения
        third_column = [
            ('Мин X:', self.controller.x_min_var, None),
            ('Мин Y:', self.controller.y_min_var, None)
        ]
        for i, (label, var, _) in enumerate(third_column):
            ttk.Label(self.curve_frame, text=label).grid(row=i, column=4, padx=5, pady=2, sticky='w')
            ttk.Entry(
                self.curve_frame,
                textvariable=var,
                width=8
            ).grid(row=i, column=5, padx=5, pady=2, sticky='w')

        # Четвертая колонка: Максимальные значения
        fourth_column = [
            ('Макс X:', self.controller.x_max_var, None),
            ('Макс Y:', self.controller.y_max_var, None)
        ]
        for i, (label, var, _) in enumerate(fourth_column):
            ttk.Label(self.curve_frame, text=label).grid(row=i, column=6, padx=5, pady=2, sticky='w')
            ttk.Entry(
                self.curve_frame,
                textvariable=var,
                width=8
            ).grid(row=i, column=7, padx=5, pady=2, sticky='w')

        # Кнопка добавления линии
        ttk.Button(
            self.curve_frame,
            text='Добавить линию',
            command=self.add_curve
        ).grid(row=len(first_column), column=0, columnspan=2, padx=5, pady=5, sticky='ew')

    def update_marker_style_state(self):
        """Обновление состояния Combobox для стиля маркеров"""
        if self.controller.show_marker_var.get():
            self.marker_style_combobox.configure(state='readonly')
        else:
            self.marker_style_combobox.configure(state='disabled')
            self.controller.marker_var.set('')

    def add_curve(self):
        self.controller.add_curve()

    def create_curve_list(self):

            # Заменяем Listbox на Treeview
        self.curve_tree = ttk.Treeview(self, columns=('select', 'label'), show='headings', height=10)
        self.curve_tree.heading('select', text='')
        self.curve_tree.heading('label', text='Кривые')
        self.curve_tree.column('select', width=30, stretch=NO)
        self.curve_tree.column('label', width=200)
        self.curve_tree.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')

        # Кнопки управления
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=1, padx=5, pady=5, sticky='n')
        
        ttk.Button(btn_frame, text='Удалить выбранные', command=self.remove_curve).pack(pady=2)
        ttk.Button(btn_frame, text='Вверх', command=lambda: self.move_curve(-1)).pack(pady=2)
        ttk.Button(btn_frame, text='Вниз', command=lambda: self.move_curve(1)).pack(pady=2)

    def remove_curve(self):
        # self.controller.remove_curve()
        selected = self.curve_tree.selection()
        for item in reversed(selected):
            idx = int(item)
            if idx < len(self.controller.curves):
                del self.controller.curves[idx]
            else:
                del self.controller.theory_curves[idx - len(self.controller.curves)]
        self.update_curve_list()

    def create_plot_buttons(self):
        plot_frame = ttk.Frame(self)
        plot_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        buttons = [
            ('Построить график', self.build_plot),
            ('Экспортировать данные', self.export_data)
        ]
        
        for text, command in buttons:
            ttk.Button(plot_frame, text=text, command=command).pack(side=LEFT, padx=5)

    def build_plot(self):
        try:
            self.controller.build_plot()
            logger.info("График успешно построен")  # Логируем успешное построение графика
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось построить график: {str(e)}')
            logger.error(f"Ошибка при построении графика: {str(e)}")  # Логируем ошибку

    def export_data(self):
        try:
            self.controller.export_data()
            logger.info("Данные успешно экспортированы")  # Логируем успешный экспорт данных
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось экспортировать данные: {str(e)}')
            logger.error(f"Ошибка при экспорте данных: {str(e)}")  # Логируем ошибку

    def create_interactive_plot(self):
        try:
            self.controller.create_interactive_plot()
            logger.info("Интерактивный график успешно создан")  # Логируем успешное создание интерактивного графика
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось создать интерактивный график: {str(e)}')
            logger.error(f"Ошибка при создании интерактивного графика: {str(e)}")  # Логируем ошибку

    def create_graph_settings(self):

        graph_settings_frame = ttk.LabelFrame(self, text="Настройки графика")
        graph_settings_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # Первая колонка - основные настройки
        left_settings = [
            ('Заголовок графика:', self.controller.title_var),
            ('Подпись оси X:', self.controller.xlabel_var),
            ('Подпись оси Y:', self.controller.ylabel_var),
            ('Тема графика:', self.controller.style_var)
        ]
        
        for i, (label, var) in enumerate(left_settings):
            ttk.Label(graph_settings_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            if label == 'Тема графика:':
                style_values = ['default', 'bmh', 'classic', 'dark_background', 'fast',
                                'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn-v0_8']
                ttk.Combobox(graph_settings_frame, textvariable=var,
                             values=style_values).grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                ttk.Entry(graph_settings_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=5, sticky='w')
        
        # Вторая колонка - настройки шрифта и сетки
        font_settings = [
            ('Шрифт:', self.controller.font_var, ['Arial', 'Times New Roman', 'Helvetica', 'Courier']),
            ('Размер шрифта:', self.controller.font_size_var, ['8', '10', '12', '14', '16', '18', '20']),
            ('Тип сетки:', self.controller.grid_type_var, ['Нет', 'Основная', 'Дополнительная', 'Обе']),
            ('Стиль:', self.controller.font_style_var, ['normal', 'italic', 'bold'])
        ]
        
        for i, (label, var, values) in enumerate(font_settings):
            ttk.Label(graph_settings_frame, text=label).grid(row=i, column=2, padx=5, pady=5, sticky='w')
            ttk.Combobox(graph_settings_frame, textvariable=var,
                         values=values).grid(row=i, column=3, padx=5, pady=5, sticky='w')
        
        # Третья колонка - греческие символы
        ttk.Label(graph_settings_frame, text='Символы:').grid(row=0, column=4, padx=5, pady=5, sticky='w')
        symbols_entry = ttk.Entry(graph_settings_frame, textvariable=self.controller.symbols_var, width=30, state='readonly')
        symbols_entry.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        self.enable_copy_paste(symbols_entry)
        
        # Чекбокс для правой оси
        ttk.Checkbutton(graph_settings_frame, text='Показывать правую ось',
                         variable=self.controller.show_right_axis).grid(row=5, column=0,
                                                                        padx=5, pady=5, sticky='w')
        ttk.Checkbutton(graph_settings_frame, text='Использовать LaTeX',
                         variable=self.controller.use_latex_var).grid(row=5, column=1,
                                                                      padx=5, pady=5, sticky='w')

    def update_column_menus(self):
        """Обновление значений в выпадающих списках для осей X и Y"""
        if self.controller.data_frame is None or self.controller.data_frame.empty:
            logger.warning("Попытка обновить меню столбцов без загруженных данных")
            return

        # Получаем список колонок из загруженного DataFrame
        columns = self.controller.data_frame.columns.tolist()
        logger.info(f"Обновление меню столбцов: {columns}")

        # Обновляем значения в выпадающих списках
        if self.x_menu:
            self.x_menu['values'] = columns
        if self.y_menu:
            self.y_menu['values'] = columns

    def update_curve_list(self):

        self.curve_tree.delete(*self.curve_tree.get_children())
        # Добавление кривых с чекбоксами
        for idx, curve in enumerate(self.controller.curves + self.controller.theory_curves):
            self.curve_tree.insert('', 'end', iid=idx, values=('◻', f"{curve['label']} ({curve['x']} vs {curve['y']})"))

    def move_curve(self, direction):
        selected = self.curve_tree.selection()
        if selected:
            idx = int(selected[0])
            new_idx = idx + direction
            if 0 <= new_idx < len(self.controller.curves):
                self.controller.curves.insert(new_idx, self.controller.curves.pop(idx))
                self.update_curve_list()

    def enable_copy_paste(self, widget):
        """
        Добавляет функциональность копирования, вставки и вырезания текста
        для указанного виджета.
        :param widget: Виджет ввода (например, Entry или Text).
        """
        widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
        widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))
        widget.bind("<Control-x>", lambda e: widget.event_generate("<<Cut>>"))
