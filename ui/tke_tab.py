import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import logging
import pandas as pd

# Инициализация логгера
logger = logging.getLogger('DataAnalyzer')

class TkeTab(ttk.Frame):
    def __init__(self, parent, controller):
        """
        Инициализация вкладки "Автокорреляция и Спектр ТКЭ".
        :param parent: Родительский виджет.
        :param controller: Контроллер приложения (UI).
        """
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """
        Создание интерфейса вкладки.
        """
        # Фрейм для кнопок
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, padx=10, pady=10)

        # Кнопка "Фильтровать данные"
        # ttk.Button(button_frame, text="Фильтровать данные", command=self.open_filter_window).pack(side=LEFT, padx=5)

        # Кнопка "Получить спектр ТКЭ"
        ttk.Button(button_frame, text="Получить спектр ТКЭ", command=self.calculate_tke_spectrum).pack(side=LEFT, padx=5)

    # def open_filter_window(self):
    #     """
    #     Открытие окна фильтрации (аналогично DataTab).
    #     """
    #     if not hasattr(self.controller, 'data_tab') or self.controller.data_tab is None:
    #         messagebox.showerror('Ошибка', 'Вкладка "Данные" не доступна')
    #         logger.error('Попытка открыть окно фильтрации без доступной вкладки "Данные"')
    #         return

    #     # Вызываем метод фильтрации из вкладки "Данные"
    #     self.controller.data_tab.open_filter_window()

    def calculate_tke_spectrum(self):
        """
        Расчет спектра турбулентной кинетической энергии (ТКЭ).
        """
        if self.controller.data_frame is None:
            messagebox.showwarning('Предупреждение', 'Сначала загрузите данные')
            return

        try:
            # Получаем список колонок Centroid для выбора оси
            centroid_columns = [col for col in self.controller.data_frame.columns if 'Centroid' in col]
            if not centroid_columns:
                messagebox.showwarning('Предупреждение', 'В данных не найдены колонки Centroid')
                return

            # Создаем окно для выбора параметров расчета спектра ТКЭ
            tke_window = ttk.Toplevel(self)
            tke_window.title('Настройки расчета спектра ТКЭ')
            tke_window.geometry('600x550')

            # Фрейм для выбора оси
            axis_frame = ttk.LabelFrame(tke_window, text="Выбор оси для расчета")
            axis_frame.pack(fill=X, padx=10, pady=10)

            # Переменная для хранения выбранной оси
            axis_var = ttk.StringVar()

            # Выпадающий список для выбора оси
            ttk.Label(axis_frame, text="Выберите ось:").pack(anchor=W, padx=5, pady=5)
            axis_menu = ttk.Combobox(axis_frame, textvariable=axis_var, values=centroid_columns)
            axis_menu.pack(fill=X, padx=5, pady=5)
            axis_menu.current(0) if centroid_columns else None

            # Фрейм для выбора функций
            functions_frame = ttk.LabelFrame(tke_window, text="Выбор функций для анализа")
            functions_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

            # Получаем все колонки данных кроме Centroid
            function_columns = [col for col in self.controller.data_frame.columns if 'Centroid' not in col]

            # Создаем переменные для хранения выбранных функций
            function_vars = {}

            # Добавляем чекбоксы для каждой функции
            ttk.Label(functions_frame, text="Выберите функции для анализа:").pack(anchor=W, padx=5, pady=5)

            canvas = tk.Canvas(functions_frame)
            scrollbar = ttk.Scrollbar(functions_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for col in function_columns:
                var = tk.BooleanVar(value=True)
                function_vars[col] = var
                ttk.Checkbutton(scrollable_frame, text=col, variable=var).pack(anchor=W, padx=5, pady=2)

            # Фрейм для кнопок
            button_frame = ttk.Frame(tke_window)
            button_frame.pack(fill=X, padx=10, pady=10)

            def process_tke():
                selected_axis = axis_var.get()
                selected_functions = [col for col, var in function_vars.items() if var.get()]

                if not selected_axis or not selected_functions:
                    messagebox.showwarning('Предупреждение', 'Выберите ось и хотя бы одну функцию')
                    return

                try:
                    # Расчет спектра ТКЭ с использованием контроллера
                    tke_data = self.controller.tke_calculator.calculate_tke_spectrum(
                        self.controller.data_frame,
                        selected_axis,
                        selected_functions
                    )

                    # Уведомление об успешном расчете
                    messagebox.showinfo('Успех', 'Спектр ТКЭ успешно рассчитан')
                    logger.info("Спектр ТКЭ успешно рассчитан")

                    # Объединение данных спектра ТКЭ с текущим DataFrame
                    self.controller.data_frame = pd.concat([self.controller.data_frame, tke_data], axis=1)

                    # Обновление интерфейса или экспорт данных в графики (если это необходимо)
                    self.controller.update_tabs()

                    tke_window.destroy()
                except Exception as e:
                    messagebox.showerror('Ошибка', f'Не удалось рассчитать спектр ТКЭ: {str(e)}')
                    logger.error(f'Ошибка при расчете спектра ТКЭ: {str(e)}')

            # Кнопка "Рассчитать"
            ttk.Button(button_frame, text="Рассчитать", command=process_tke).pack(side=LEFT, padx=5)

        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось открыть окно расчета спектра ТКЭ: {str(e)}')
