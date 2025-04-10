from ui.ui import DataAnalyzer as UI
from logger import logger

if __name__ == "__main__":
    try:
        # Создаем экземпляр приложения
        app = UI()

        # Запускаем приложение
        app.run()
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}")
