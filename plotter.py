import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import numpy as np
from logger import logger


class Plotter:
    def __init__(self, controller=None):
        self.fig = None
        self.controller = controller  # Ссылка на контроллер для доступа к данным

        # Настройки графика (перенесены из settings)
        self.style = "default"  # Стиль графика
        self.font_family = "Arial"  # Шрифт
        self.font_size = 12  # Размер шрифта
        self.font_style = "normal"  # Стиль шрифта (обычный)
        self.use_latex = False  # Использовать ли LaTeX для рендеринга текста
        self.show_right_axis = False  # Показывать ли правую ось Y
        self.x_scale = "linear"  # Масштаб оси X (линейный или логарифмический)
        self.y_scale = "linear"  # Масштаб оси Y (линейный или логарифмический)
        self.grid_type = "both"  # Тип сетки ('major', 'minor', 'both', 'none')
        self.legend_position = "upper right"  # Позиция легенды
        self.xlabel = "Ось X"  # Подпись оси X
        self.ylabel = "Ось Y"  # Подпись оси Y (левая ось)
        self.ylabel_right = "Правая ось Y"  # Подпись правой оси Y (если есть)
        self.title = "График"  # Заголовок графика
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None

    def update_settings(self, settings):
        """Обновляет настройки графика"""
        self.style = settings.get('style', self.style)
        self.font_family = settings.get('font', self.font_family)
        self.font_size = settings.get('font_size', self.font_size)
        self.font_style = settings.get('font_style', self.font_style)
        self.use_latex = settings.get('use_latex', self.use_latex)
        self.show_right_axis = settings.get('show_right_axis', self.show_right_axis)
        self.grid_type = settings.get('grid_type', self.grid_type)
        self.x_min = settings.get('x_min', None)
        self.x_max = settings.get('x_max', None)
        self.y_min = settings.get('y_min', None)
        self.y_max = settings.get('y_max', None)
        self.xlabel = settings.get('xlabel', self.xlabel)
        self.ylabel = settings.get('ylabel', self.ylabel)
        self.title = settings.get('title', self.title)
        self.x_scale = settings.get('x_scale', self.x_scale)
        self.y_scale = settings.get('y_scale', self.y_scale)
        self.legend_position = settings.get('legend_position', self.legend_position)

    def build_static_plot(self, data_frame, experimental_curves):
        """
        Построение статического графика с поддержкой теоретических данных.
        """
        try:
            # Применяем стиль графика
            plt.style.use(self._get_valid_style(self.style))

            # Настройка шрифтов и LaTeX
            self._configure_fonts()

            # Объединяем экспериментальные и теоретические кривые
            all_curves = experimental_curves + self.controller.theory_curves

            # Создаем фигуру и оси
            self.fig, ax1 = plt.subplots(figsize=(6, 6))
            ax2 = ax1.twinx() if self.show_right_axis else None

            # Настройка осей и сетки
            self._configure_axes(ax1, ax2)
            self._configure_grid(ax1)

            # Построение всех кривых
            for curve in all_curves:
                self._plot_single_curve(ax1, ax2, curve, data_frame)

            # Настройка легенды и подписей
            self._set_labels_and_legend(ax1, ax2)

            return self.fig

        except Exception as e:
            logger.error(f"Ошибка построения графика: {str(e)}")
            raise

    def _get_valid_style(self, style_name):
        """Проверяет и возвращает допустимый стиль графика"""
        return style_name if style_name in plt.style.available else "default"

    def _configure_fonts(self):
        """Настраивает параметры шрифтов"""
        plt.rcParams.update({
            'font.family': self.font_family,
            'font.size': float(self.font_size),
            'font.style': self.font_style,
            "text.usetex": self.use_latex,
            "axes.titlesize": float(self.font_size) + 2,
        })

        if self.use_latex:
            plt.rcParams.update({
                "text.usetex": True,
                "text.latex.preamble": r"""
                    \usepackage[utf8]{inputenc}
                    \usepackage[T2A]{fontenc}
                    \usepackage[russian]{babel}
                """
            })

    def _configure_axes(self, ax1, ax2):
        """Настраивает пределы и масштаб осей"""
        # Используем атрибуты класса вместо локальных переменных
        x_min, x_max = self.x_min, self.x_max
        y_min, y_max = self.y_min, self.y_max

        if x_min not in (None, ''):
            ax1.set_xlim(left=float(x_min))
        if x_max not in (None, ''):
            ax1.set_xlim(right=float(x_max))
        
        if y_min not in (None, ''):
            ax1.set_ylim(bottom=float(y_min))
        if y_max not in (None, ''):
            ax1.set_ylim(top=float(y_max))

        # Масштаб осей
        ax1.set_xscale(self.x_scale)
        ax1.set_yscale(self.y_scale)
        
        if ax2:
            ax2.set_yscale(self.y_scale)

    def _configure_grid(self, ax):
        """Настраивает отображение сетки"""
        grid_mapping = {
            'нет': 'none',
            'основная': 'major',
            'дополнительная': 'minor',
            'обе': 'both'
        }
        grid_type = grid_mapping.get(self.grid_type.lower(), 'none')
        
        if grid_type == 'major':
            ax.grid(True, which='major')
        elif grid_type == 'minor':
            ax.grid(True, which='minor')
        elif grid_type == 'both':
            ax.grid(True, which='both')

    def _plot_single_curve(self, ax1, ax2, curve, data_frame):
        """Отрисовывает отдельную кривую"""
        try:
            if curve.get('is_theory'):
                x_data = curve['x']
                y_data = curve['y']
            else:
                x_data = data_frame[curve['x']]
                y_data = data_frame[curve['y']]

            if self.x_scale == "log" and (np.array(x_data) <= 0).any():
                raise ValueError("Ось X содержит неположительные значения для логарифмического масштаба")
            
            if self.y_scale == "log" and (np.array(y_data) <= 0).any():
                raise ValueError("Ось Y содержит неположительные значения для логарифмического масштаба")

            ax = ax2 if curve.get('axis') == 'right' and ax2 else ax1

            plot_kwargs = {
                'color': curve.get('color', 'blue'),
                'linestyle': curve.get('style', '-'),
                'linewidth': curve.get('line_width', 1.0),
                'marker': curve.get('marker', ''),
                'label': curve.get('label', 'Без названия')
            }

            ax.plot(x_data, y_data, **plot_kwargs)

        except KeyError as e:
            logger.error(f"Отсутствует колонка данных: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Ошибка данных: {str(e)}")
            raise

    def _set_labels_and_legend(self, ax1, ax2):
        """Добавляет подписи и легенду"""
        try:
            ax1.set_xlabel(self._format_label(self.xlabel))
            ax1.set_ylabel(self._format_label(self.ylabel))
            
            if ax2:
                ax2.set_ylabel(self._format_label(self.ylabel_right))

            ax1.set_title(self._format_label(self.title))

            handles, labels = ax1.get_legend_handles_labels()
            
            if ax2:
                h2, l2 = ax2.get_legend_handles_labels()
                handles += h2
                labels += l2

            if handles and labels:
                ax1.legend(handles, labels, loc=self.legend_position)

        except Exception as e:
            logger.error(f"Ошибка оформления графика: {str(e)}")

    def _format_label(self, text):
        """Форматирует текст меток с учетом LaTeX"""
        if self.use_latex and text:
            if any("а" <= char <= "я" or "А" <= char <= "Я" for char in text):
                # Для русского текста оставляем обычный текст (без математического режима)
                return text
            # Для латиницы и формул используем математический режим
            return rf"${text}$"
        return text
