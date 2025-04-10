from logger import logger

class DataProcessor:
    def process_data(self, data_frame, selected_columns, aggregation_method):
        try:
            # Обработка данных с помощью выбранного метода агрегации
            if aggregation_method == 'mean':
                processed_data = data_frame[selected_columns].mean().to_frame().T
            elif aggregation_method == 'median':
                processed_data = data_frame[selected_columns].median().to_frame().T
            elif aggregation_method == 'sum':
                processed_data = data_frame[selected_columns].sum().to_frame().T
            else:
                raise ValueError("Неподдерживаемый метод агрегации")
            
            return processed_data
        except Exception as e:
            logger.error(f"Ошибка при обработке данных: {str(e)}")
            raise

    def filter_data(self, data_frame, selected_axis, threshold):
        try:
            # Фильтруем данные по выбранной оси
            filtered_data = data_frame[data_frame[selected_axis] <= threshold].copy()
            return filtered_data
        except Exception as e:
            logger.error(f"Ошибка при фильтрации данных: {str(e)}")
            raise

    def group_data(self, data_frame, group_by_column, selected_columns):
        try:
            # Группируем данные и вычисляем среднее для каждой функции
            grouped_data = data_frame.groupby(group_by_column)[selected_columns].mean().reset_index()
            return grouped_data
        except Exception as e:
            logger.error(f"Ошибка при группировке данных: {str(e)}")
            raise
