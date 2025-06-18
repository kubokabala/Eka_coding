import osmnx as ox
import pandas as pd

def get_marina_count_and_save_to_csv(city_name="Санкт-Петербург", output_filename="marinas.csv"):
    """
    Извлекает количество марин (leisure=marina) из OpenStreetMap для заданного города
    и сохраняет результат в CSV файл.

    Args:
        city_name (str, optional): Название города для поиска. Defaults to "Санкт-Петербург".
        output_filename (str, optional): Имя файла для сохранения CSV. Defaults to "marinas.csv".
    """
    try:
        # 1. Получаем геометрию города.  Важно, чтобы город находился osmnx
        gdf = ox.geocode_to_gdf(city_name)
        if gdf.empty:
            print(f"Ошибка: Не удалось найти город '{city_name}' в OpenStreetMap.")
            return

        # 2. Запрашиваем данные о маринах из OSM. Используем polygon для ограничивания поиска территорией города
        tags = {"leisure": "marina"}
        marinas = ox.features_from_polygon(gdf['geometry'].iloc[0], tags)  # Используем геометрию города

        # 3. Получаем количество марин
        marina_count = len(marinas)

        # 4. Создаем DataFrame для записи в CSV.  Записываем название города и количество
        data = {'city': [city_name], 'marina_count': [marina_count]}
        df = pd.DataFrame(data)

        # 5. Сохраняем DataFrame в CSV файл
        df.to_csv(output_filename, index=False)

        print(f"Найдено {marina_count} марин в городе {city_name}.")
        print(f"Результат сохранен в файл: {output_filename}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    get_marina_count_and_save_to_csv()