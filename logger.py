import logging

def init_logger():
    """
    Инициализация логгера.
    """
    logger = logging.getLogger('DataAnalyzer')  # Название логгера
    logger.setLevel(logging.INFO)  # Уровень логирования (INFO)

    # Создаем обработчик для записи в файл
    file_handler = logging.FileHandler('logs.log', mode='w', encoding='utf-8')  # Добавляем encoding='utf-8'
    file_handler.setLevel(logging.INFO)  # Уровень логирования для файла

    # Создаем форматтер для сообщений лога
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    return logger

# Инициализация глобального логгера
logger = init_logger()
