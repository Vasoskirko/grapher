import pandas as pd
from logger import logger
import csv

class DataLoader:
    # def load_csv(self, file_path):
    #     """Универсальный метод загрузки CSV"""
    #     try:
    #         # Автоопределение разделителя
    #         with open(file_path, 'r') as f:
    #             dialect = csv.Sniffer().sniff(f.read(1024))
    #             f.seek(0)
    #             return pd.read_csv(f, delimiter=dialect.delimiter)
    #     except Exception as e:
    #         logger.error(f"Ошибка загрузки CSV: {str(e)}")
    #         raise
    def load_csv(self, file_path):
        try:
            # Загружаем CSV в DataFrame
            data_frame = pd.read_csv(file_path)
            
            # Проверяем, что файл не пустой
            if data_frame.empty:
                raise ValueError("Файл не содержит данных")
            
            return data_frame
        except FileNotFoundError:
            raise FileNotFoundError("Файл не найден")
        except pd.errors.EmptyDataError:
            raise pd.errors.EmptyDataError("Файл пуст")
        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f"Ошибка парсинга: {str(e)}")
        except Exception as e:
            raise Exception(f"Неизвестная ошибка при загрузке CSV: {str(e)}")
        
    def load_theoretical_data(self, file_path):
        """Загрузка теоретических данных через общий CSV loader"""
        return self.load_csv(file_path)