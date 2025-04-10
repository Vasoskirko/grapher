import pandas as pd
import numpy as np
from logger import logger

class DataProcessor:
    def __init__(self):
        self.cell_sizes_calculated = False
        self.rounded_columns = []
        self.unique_values = {}

    def round_columns(self, df: pd.DataFrame, columns: list, decimals: int) -> pd.DataFrame:
        """Округляет только выбранные колонки и сортирует по X -> Y -> Z."""
        try:
            # Округление только выбранных колонок
            for col in columns:
                if col not in df.columns:
                    raise ValueError(f"Колонка {col} не найдена")
                df[col] = df[col].round(decimals)

            # Сортировка по X/Y/Z (даже если они не округлялись)
            required_columns = ['X (m)', 'Y (m)', 'Z (m)']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Для сортировки нужны колонки X/Y/Z (m)")
            
            df = df.sort_values(by=required_columns, ascending=[True, True, True])
            logger.info(f"Данные отсортированы по {required_columns}")
            return df

        except Exception as e:
            logger.error(f"Ошибка при округлении: {str(e)}")
            raise


    def calculate_cell_sizes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Рассчитывает размеры ячеек на очищенных данных."""
        try:
            # Проверка наличия колонок
            required_columns = ['X (m)', 'Y (m)', 'Z (m)']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Отсутствуют координатные колонки X/Y/Z (m)")
            
            # Рассчитываем размеры для каждой оси
            for axis in required_columns:
                sorted_values = np.sort(df[axis].unique())
                if len(sorted_values) < 2:
                    raise ValueError(f"Недостаточно данных для расчета размеров по {axis}")
                
                # Размеры ячеек (расстояние между центрами)
                sizes = [sorted_values[i] - sorted_values[i-1] for i in range(1, len(sorted_values))]
                sizes = [sizes[0]] + sizes  # Первая ячейка после стенки
                
                # Сопоставляем размерам значения координат
                size_col = f"size_{axis.split(' ')[0]}"
                df[size_col] = df[axis].map(dict(zip(sorted_values, sizes)))
            
            # Вес ячейки = объем (size_X * size_Y * size_Z)
            df["weight"] = df[['size_X', 'size_Y', 'size_Z']].product(axis=1)
            logger.info("Размеры ячеек и вес рассчитаны")
            return df
        
        except Exception as e:
            logger.error(f"Ошибка расчета ячеек: {str(e)}")
            raise

    def process_data(self, df: pd.DataFrame, group_column: str, agg_method: str, use_weights: bool, target_columns: list) -> pd.DataFrame:
        """Основной метод агрегации данных."""
        # Валидация
        if use_weights and not self.cell_sizes_calculated:
            raise ValueError("Сначала рассчитайте размеры ячеек!")

        # Расчет весов
        if use_weights:
            weight_cols = ['size_X', 'size_Y', 'size_Z']
            if not all(col in df.columns for col in weight_cols):
                raise ValueError("Колонки для расчета весов отсутствуют!")

            df["weight"] = df[weight_cols].product(axis=1)
            agg_func = lambda g: pd.Series({
                col: np.average(g[col], weights=g["weight"]) for col in target_columns
            })
        else:
            agg_func = lambda g: g[target_columns].agg(agg_method)

        return df.groupby(group_column).apply(agg_func).reset_index()

    def validate_columns(self, df: pd.DataFrame, required_columns: list):
        """Проверяет наличие необходимых колонок в DataFrame."""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Отсутствуют необходимые колонки: {', '.join(missing)}")

    def add_weight_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавляет колонку с весовыми коэффициентами."""
        required_columns = ['size_X', 'size_Y', 'size_Z']
        self.validate_columns(df, required_columns)

        # Расчет веса как произведения размеров ячеек
        df["weight"] = df[required_columns].product(axis=1)
        return df

    def aggregate_data(self, df: pd.DataFrame, group_column: str, target_columns: list) -> pd.DataFrame:
        """Усредняет данные по выбранной оси с учетом весов."""
        if "weight" not in df.columns:
            raise ValueError("Сначала рассчитайте веса!")
        
        grouped = df.groupby(group_column).apply(
            lambda g: pd.Series({
                col: np.average(g[col], weights=g["weight"]) for col in target_columns
            })
        )
        return grouped.reset_index()

    def calculate_unique_cells(self, df: pd.DataFrame) -> int:
        """
        Подсчитывает количество уникальных ячеек на основе размеров X, Y, Z.
        
        :param df: DataFrame с рассчитанными размерами ячеек
        :return: Количество уникальных ячеек
        """
        unique_x = df['X (m)_rounded'].nunique() if 'X (m)_rounded' in df.columns else 0
        unique_y = df['Y (m)_rounded'].nunique() if 'Y (m)_rounded' in df.columns else 0
        unique_z = df['Z (m)_rounded'].nunique() if 'Z (m)_rounded' in df.columns else 0

        total_cells = unique_x * unique_y * unique_z
        print(f"Количество уникальных ячеек: {total_cells}")
        
        return total_cells
    
    def filter_wall_values(self, df: pd.DataFrame, walls: dict) -> pd.DataFrame:
        """Удаляет строки с координатами стенок."""
        try:
            # Проверка наличия колонок
            required_columns = ['X (m)', 'Y (m)', 'Z (m)']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Отсутствуют координатные колонки X/Y/Z (m)")
            
            # Фильтрация данных
            mask = (
                df['X (m)'].isin(walls['x']) |
                df['Y (m)'].isin(walls['y']) |
                df['Z (m)'].isin(walls['z'])
            )
            filtered_df = df[~mask].copy()
            
            logger.info(f"Удалено строк с стенками: {len(df) - len(filtered_df)}")
            return filtered_df
        
        except Exception as e:
            logger.error(f"Ошибка фильтрации стенок: {str(e)}")
            raise
