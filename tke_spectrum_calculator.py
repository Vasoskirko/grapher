import numpy as np
import pandas as pd
from logger import logger
from scipy.fft import fft, fftfreq

class TKE_SpectrumCalculator:
    def calculate_tke_spectrum(self, data_frame, selected_axis, selected_functions):
        """
        Рассчитывает спектр турбулентной кинетической энергии (ТКЭ) для выбранных функций.

        :param data_frame: DataFrame с исходными данными.
        :param selected_axis: Ось для расчета (например, 'Centroid[X]', 'Centroid[Y]', 'Centroid[Z]').
        :param selected_functions: Список функций для расчета спектра ТКЭ.
        :return: DataFrame с результатами расчета (волновые числа k и спектр энергии E_k).
        """
        try:
            # Проверка входных данных
            if data_frame is None or data_frame.empty:
                raise ValueError("DataFrame пуст или не загружен.")
            if selected_axis not in data_frame.columns:
                raise ValueError(f"Выбранная ось '{selected_axis}' отсутствует в DataFrame.")
            if not all(func in data_frame.columns for func in selected_functions):
                missing_funcs = [func for func in selected_functions if func not in data_frame.columns]
                raise ValueError(f"Следующие функции отсутствуют в DataFrame: {missing_funcs}")

            # Создаем DataFrame для хранения результатов
            tke_data = pd.DataFrame()

            # Для каждой выбранной функции рассчитываем спектр
            for function in selected_functions:
                logger.info(f"Рассчитываем спектр для функции '{function}' по оси '{selected_axis}'.")

                # Получаем данные для текущей функции
                r_values = np.sort(data_frame[selected_axis].values)  # пространственная координата
                R_values = data_frame[function].values  # автокорреляционная функция
                N = len(r_values)
                half_N = N //2
                 # Используем только первую половину данных
                r_half = r_values[:half_N]
                R_half = R_values[:half_N]

                if len(r_half) < 2:
                    raise ValueError("Недостаточно данных после обрезки")
                
                delta_r = r_half[1] - r_half[0]
                print(f"Уникальные по оси '{selected_axis}' = '{r_values}'")

                # Вычисляем волновые числа и спектр энергии
                
                # k = 2*np.pi * np.fft.fftfreq(len(r_values), d=delta_r)
                
                    # Расчет FFT для усеченных данных
                k = 2 * np.pi * fftfreq(half_N, d=delta_r)
                fft_result = fft(R_half)
                E_k = np.abs(fft_result) ** 2 / (2 * np.pi * half_N) 

                # E_k = np.abs(np.fft.fft(R_values)) ** 2 / (2 * np.pi * len(R_values))
                # E_k = np.abs(fftfreq(fft(R_values))) ** 2 / (2 * np.pi * len(R_values))

                # Выбираем только положительные волновые числа (кроме нулевого)
                k_positive = k[k > 0]
                E_k_positive = E_k[k > 0]

                # Добавляем результаты в DataFrame
                if len(k_positive) > 0:
                    k_col_name = f'k_{function}'  # Имя колонки для волновых чисел
                    E_col_name = f'E_{function}'  # Имя колонки для спектра энергии

                    tke_data[k_col_name] = k_positive
                    tke_data[E_col_name] = E_k_positive

            logger.info("Расчет спектра ТКЭ успешно завершен.")
            return tke_data

        except Exception as e:
            logger.error(f"Ошибка при расчете спектра ТКЭ: {str(e)}")
            raise
