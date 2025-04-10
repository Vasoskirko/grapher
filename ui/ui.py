import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd
from logger import logger
from ui.data_tab import DataTab
from ui.plot_tab import PlotTab
from data_loader import DataLoader
from ui.tke_tab import TkeTab
from data_processor import DataProcessor
from tke_spectrum_calculator import TKE_SpectrumCalculator
from plotter import Plotter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation
import plotly.graph_objects as go  # Построение интерактивных графиков Plotly
from plotly.subplots import make_subplots


class DataAnalyzer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title('Графёр')
        self.geometry('1140x1140')
        self.style = ttk.Style("flatly")
        self.data_frame = None

        # Инициализация вспомогательных классов
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()
        self.tke_calculator = TKE_SpectrumCalculator()
        self.plotter = Plotter(controller=self)

        # Переменные для взаимодействия с интерфейсом
        self.initialize_variables()

        # Создание интерфейса
        self.create_widgets()
        self.create_menu()
        self.register_dnd()
        
    def initialize_variables(self):
        """Инициализация переменных"""
        # Переменные для графиков и настроек
        self.x_var = ttk.StringVar()
        self.y_var = ttk.StringVar()
        self.curve_label_var = ttk.StringVar()
        self.color_var = ttk.StringVar(value='blue')
        self.line_style_var = ttk.StringVar(value='-')
        self.axis_var = ttk.StringVar(value='left')
        self.marker_var = ttk.StringVar(value='o')
        self.line_width_var = tk.DoubleVar(value=1.0)
        self.show_marker_var = tk.BooleanVar(value=False)

        # Переменные для настроек графика
        self.title_var = ttk.StringVar()
        self.xlabel_var = ttk.StringVar()
        self.ylabel_var = ttk.StringVar()
        self.style_var = ttk.StringVar(value='default')
        self.x_scale_var = tk.StringVar(value='linear')
        self.y_scale_var = tk.StringVar(value='linear')

        # Переменные для теоретических данных и спектра ТКЭ
        self.use_latex_var = tk.BooleanVar(value=False)
        self.theory_data = None
        self.theory_curves = []

        # Настройки шрифта и сетки
        self.font_var = tk.StringVar(value='Arial')
        self.font_size_var = tk.StringVar(value='12')
        self.grid_type_var = tk.StringVar(value='Нет')
        self.font_style_var = tk.StringVar(value='normal')
        self.symbols_var = tk.StringVar(value='αβγδεζηθικλμνξπρστυφχψω')
        
        # Пределы осей и положение легенды
        self.x_min_var = tk.StringVar()
        self.x_max_var = tk.StringVar()
        self.y_min_var = tk.StringVar()
        self.y_max_var = tk.StringVar()

        # Прочие переменные
        self.show_right_axis = tk.BooleanVar(value=False)
        
        self.curves = []
        self.legend_position_var = ttk.StringVar(value='upper right')

    def create_widgets(self):
        """Создание вкладок и статусной строки"""
        # Создание вкладок
        notebook_frame = ttk.Notebook(self)

        # Вкладка "Данные"
        self.data_tab = DataTab(notebook_frame, controller=self)
        notebook_frame.add(self.data_tab, text="Данные")

        # Вкладка "Графики"
        self.plot_tab = PlotTab(notebook_frame, controller=self)
        notebook_frame.add(self.plot_tab, text="Графики")

        notebook_frame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        # Создание строки состояния
        self.status_bar = ttk.Label(self, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Вкладка "Автокорреляция и Спектр ТКЭ"
        self.tke_tab = TkeTab(notebook_frame, controller=self)
        notebook_frame.add(self.tke_tab, text="Автокорреляция и Спектр ТКЭ")

    def load_theoretical_data(self):
        """Загрузка теоретических данных (аналогично основным)"""
        file_path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if file_path:
            try:
                self.theory_data = self.data_loader.load_csv(file_path)
                self.plot_tab.theory_info.config(
                    text=f"Теоретические данные: {self.theory_data.shape[0]} строк"
                )
                messagebox.showinfo('Успех', 'Теоретические данные загружены')
            except Exception as e:
                self.show_error(f"Ошибка загрузки теории: {str(e)}")

    def show_error(self, message):
        messagebox.showerror('Ошибка', message)
        logger.error(message)

    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        
        file_menu.add_command(label="Открыть CSV", command=self.load_csv)
        file_menu.add_command(label="Открыть XLSX", command=self.load_xlsx)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)

        # Меню "Тема"
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Тема", menu=theme_menu)

        theme_menu.add_command(label="Переключить тему", command=self.toggle_theme)

        # Меню "LaTeX"
        latex_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="LaTeX", menu=latex_menu)

        latex_menu.add_command(label="Редактор формул", command=self.create_latex_editor)

        # Устанавливаем главное меню
        self.config(menu=menubar)

   
    def load_csv(self):
        # Открытие диалогового окна для выбора файла
        file_path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if file_path:  # Проверяем, что пользователь выбрал файл
            try:
                # Загружаем данные с помощью data_loader
                self.data_frame = self.data_loader.load_csv(file_path)

                
                # Проверяем, что данные успешно загружены
                if self.data_frame is None or self.data_frame.empty:
                    logger.warning("Загруженный файл пуст или не содержит данных")
                    self.show_error("Файл пуст или не содержит данных")
                    return
                
                # Логирование первых строк для отладки
                logger.info(f"Загруженные данные:\n{self.data_frame.head()}")
                
                # Обновляем вкладки интерфейса
                self.update_tabs()
                self.data_tab.update_preview()
            except pd.errors.EmptyDataError:
                logger.error("Файл пуст или имеет неправильный формат")
                self.show_error("Файл пуст или имеет неправильный формат")
            except pd.errors.ParserError as e:
                logger.error(f"Ошибка парсинга CSV: {str(e)}")
                self.show_error(f"Ошибка парсинга CSV: {str(e)}")
            except Exception as e:
                logger.error(f"Не удалось загрузить CSV: {str(e)}")
                self.show_error(f"Ошибка: {str(e)}")
            
    def load_xlsx(self):
        """Загрузка данных из XLSX файла"""
        file_path = filedialog.askopenfilename(filetypes=[('Excel files', '*.xlsx')])
        if file_path:
            self.load_data(file_path, 'xlsx')

    def load_data(self, file_path, file_type):
        """Загрузка данных и обновление интерфейса"""
        try:
            self.data_frame = self.data_loader.load_data(file_path, file_type)
            self.update_tabs()
            self.status_bar.config(text=f"Данные загружены: {file_path}")
            messagebox.showinfo('Успех', f'Файл загружен: {file_path}')
            logger.info(f"Данные успешно загружены из файла: {file_path}")
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось загрузить файл: {str(e)}')
            logger.error(f"Ошибка при загрузке данных из файла {file_path}: {str(e)}")

    def update_tabs(self):
        """Обновление вкладок после загрузки данных"""
        if hasattr(self.data_tab, 'update_data_info'):
            self.data_tab.update_data_info()
        if hasattr(self.plot_tab, 'update_column_menus'):
            self.plot_tab.update_column_menus()

    def toggle_theme(self):
        """Переключение темы интерфейса"""
        current_theme = self.style.theme_use()
        new_theme = "darkly" if current_theme == "flatly" else "flatly"
        self.style.theme_use(new_theme)
        logger.info(f"Тема переключена на: {new_theme}")

    def create_latex_editor(self):
        """Создание редактора формул LaTeX"""
        latex_window = ttk.Toplevel(self)
        latex_window.title('Редактор LaTeX')
        latex_window.geometry('600x400')

        # Фрейм для редактирования
        edit_frame = ttk.Frame(latex_window)
        edit_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Поле ввода LaTeX
        ttk.Label(edit_frame, text="Введите формулу LaTeX:").pack(anchor=W)
        latex_input = ttk.Text(edit_frame, height=5)
        latex_input.pack(fill=X, pady=5)
        
        # Пример формулы
        latex_input.insert('1.0', r'f(x) = \frac{1}{\sigma\sqrt{2\pi}}e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}')

        # Фрейм для предпросмотра
        preview_frame = ttk.LabelFrame(latex_window, text="Предпросмотр")
        preview_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Кнопка предпросмотра
        preview_button = ttk.Button(edit_frame, text="Предпросмотр",
                                     command=lambda: self.preview_latex(latex_input.get('1.0', 'end-1c'), preview_frame))
        
        preview_button.pack(pady=5)

    def preview_latex(self, latex_text, preview_frame):
        """Предпросмотр формулы LaTeX"""
        for widget in preview_frame.winfo_children():
            widget.destroy()

        try:
            fig = plt.figure(figsize=(5, 1.5))
            fig.text(0.5, 0.5, f"${latex_text}$",
                     usetex=True, fontsize=14,
                     horizontalalignment='center',
                     verticalalignment='center')

            canvas = FigureCanvasTkAgg(fig, master=preview_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
            logger.info("Предпросмотр формулы LaTeX успешно выполнен")
        
        except Exception as e:
            error_label = ttk.Label(preview_frame, text=f"Ошибка: {str(e)}", foreground="red")
            error_label.pack(pady=10)
            logger.error(f"Ошибка при предпросмотре формулы LaTeX: {str(e)}")

    def register_dnd(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_file)

    def drop_file(self, event):
        """Обработка события перетаскивания файла"""
        file_path = event.data.strip()
        if file_path.endswith('.csv'):
            self.load_data(file_path, 'csv')
        elif file_path.endswith('.xlsx'):
            self.load_data(file_path, 'xlsx')
        else:
            messagebox.showerror('Ошибка', 'Неподдерживаемый формат файла')
            logger.error(f"Неподдерживаемый формат файла: {file_path}")

    def reset_data(self):
        """Сброс загруженных данных"""
        self.data_frame = None
        self.curves.clear()
        self.theory_curves.clear()
        self.update_tabs()
        messagebox.showinfo('Информация', 'Данные успешно сброшены')
        logger.info("Данные успешно сброшены")

    def save_plot(self):
        """Сохранение текущего графика"""
        if not hasattr(self.plotter, 'fig') or self.plotter.fig is None:
            messagebox.showwarning('Предупреждение', 'Сначала постройте график')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG files', '*.png'), ('All files', '*.*')]
        )
        if file_path:
            try:
                self.plotter.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo('Успех', f'График успешно сохранен: {file_path}')
                logger.info(f"График успешно сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror('Ошибка', f'Не удалось сохранить график: {str(e)}')
                logger.error(f"Ошибка при сохранении графика: {str(e)}")

    def export_data(self):
        """Экспорт данных в файл"""
        if self.data_frame is None:
            messagebox.showwarning('Предупреждение', 'Нет данных для экспорта')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('Excel files', '*.xlsx'), ('All files', '*.*')]
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.data_frame.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.data_frame.to_excel(file_path, index=False)
                else:
                    # Если формат не указан, сохраняем как CSV
                    if not file_path.endswith('.csv'):
                        file_path += '.csv'
                    self.data_frame.to_csv(file_path, index=False)

                messagebox.showinfo('Успех', f'Данные успешно экспортированы в файл:\n{file_path}')
                logger.info(f"Данные успешно экспортированы в файл: {file_path}")
            except Exception as e:
                messagebox.showerror('Ошибка', f'Не удалось экспортировать данные: {str(e)}')
                logger.error(f"Ошибка при экспорте данных: {str(e)}")
    
    def add_curve(self):
        """Добавление новой кривой в список кривых"""
        if self.data_frame is None:
            messagebox.showwarning('Предупреждение', 'Сначала загрузите данные')
            logger.warning("Попытка добавить кривую без загруженных данных")
            return

        try:
            # Создаем словарь с параметрами новой кривой
            curve = {
                'x': self.x_var.get(),
                'y': self.y_var.get(),
                'color': self.color_var.get(),
                'style': self.line_style_var.get(),
                'label': self.curve_label_var.get(),
                'axis': self.axis_var.get(),
                'marker': self.marker_var.get() if self.show_marker_var.get() else '',
                'line_width': self.line_width_var.get()
            }

            # Добавляем кривую в список
            self.curves.append(curve)

            # Обновляем интерфейс вкладки "Графики"
            self.plot_tab.update_curve_list()

            logger.info(f"Кривая успешно добавлена: {curve}")
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось добавить кривую: {str(e)}')
            logger.error(f"Ошибка при добавлении кривой: {str(e)}")

    def remove_curve(self):
        """Удаление выбранной кривой из списка кривых"""
        try:
            selected = self.plot_tab.curve_listbox.curselection()
            if not selected:
                messagebox.showwarning('Предупреждение', 'Сначала выберите кривую для удаления')
                return

            index = selected[0]
            if index < len(self.curves):
                # Удаляем экспериментальную кривую
                del self.curves[index]
            else:
                # Удаляем теоретическую кривую
                del self.theory_curves[index - len(self.curves)]

            # Обновляем интерфейс вкладки "Графики"
            self.plot_tab.update_curve_list()

            logger.info(f"Кривая с индексом {index} успешно удалена")
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось удалить кривую: {str(e)}')
            logger.error(f"Ошибка при удалении кривой: {str(e)}")

    def build_plot(self):
        """Построение статического графика"""
        if not self.curves:
            messagebox.showwarning('Предупреждение', 'Добавьте хотя бы одну линию')
            logger.warning("Попытка построить график без добавленных кривых")
            return

        try:
            # Настройки графика
            settings = {
                'style': self.style_var.get(),
                'font': self.font_var.get(),
                'font_size': self.font_size_var.get(),
                'font_style': self.font_style_var.get(),
                'use_latex': self.use_latex_var.get(),
                'show_right_axis': self.show_right_axis.get(),
                'grid_type': self.grid_type_var.get().lower().replace('нет', 'none'),
                'x_min': self.x_min_var.get(),
                'x_max': self.x_max_var.get(),
                'y_min': self.y_min_var.get(),
                'y_max': self.y_max_var.get(),
                'xlabel': self.xlabel_var.get(),
                'ylabel': self.ylabel_var.get(),
                'title': self.title_var.get(),
                'x_scale': self.x_scale_var.get(),
                'y_scale': self.y_scale_var.get(),
                'legend_position': self.legend_position_var.get()
            }
            # Обновляем настройки в Plotter
            self.plotter.update_settings(settings)
            # Построение графика
            fig = self.plotter.build_static_plot(self.data_frame, self.curves)

            # Отображение графика в окне Tkinter
            plot_window = tk.Toplevel(self)
            plot_window.title('График')
            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)
            toolbar = NavigationToolbar2Tk(canvas, plot_window)
            toolbar.update()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)

            logger.info("Статический график успешно построен")
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось построить график: {str(e)}')
            logger.error(f"Ошибка при построении статического графика: {str(e)}")
    def update_plot_tab(self):
        """Обновление вкладки 'Графики'"""
        if hasattr(self, 'plot_tab'):
            self.plot_tab.update_column_menus()  # Используем существующий метод
            self.plot_tab.update_curve_list()    # Обновляем список кривых
            
    def run(self):
        """Запуск главного цикла приложения"""
        logger.info("Приложение запущено")
        self.mainloop()
