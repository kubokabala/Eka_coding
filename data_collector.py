import osmnx as ox
import pandas as pd

def get_marina_details_and_save_to_csv(city_name="Санкт-Петербург", output_filename="marinas.csv"):
    """
    Извлекает подробную информацию о маринах (leisure=marina) из OpenStreetMap для заданного города
    и сохраняет результат в CSV файл, где каждая строка соответствует одной марине.

    Args:
        city_name (str, optional): Название города для поиска. Defaults to "Санкт-Петербург".
        output_filename (str, optional): Имя файла для сохранения CSV. Defaults to "marinas.csv".
    """
    try:
        # 1. Получаем геометрию города
        gdf = ox.geocode_to_gdf(city_name)
        if gdf.empty:
            print(f"Ошибка: Не удалось найти город '{city_name}' в OpenStreetMap.")
            return

        # 2. Запрашиваем данные о маринах из OSM
        tags = {"leisure": "marina"}
        marinas = ox.features_from_polygon(gdf['geometry'].iloc[0], tags)

        # 3. Подготавливаем список для хранения данных о маринах
        marina_data = []

        # 4. Итерируемся по найденным маринам и извлекаем информацию
        for i, (index, marina) in enumerate(marinas.iterrows()):  #enumerate для номера марины
            # Получаем координаты (центроид геометрии)
            if marina['geometry'].geom_type == 'Polygon': # Если полигон, то центроид
                lon = marina['geometry'].centroid.x
                lat = marina['geometry'].centroid.y
            elif marina['geometry'].geom_type == 'Point': # Если точка, то просто координаты
                lon = marina['geometry'].x
                lat = marina['geometry'].y
            else:
                lon = None
                lat = None

            # Извлекаем информацию о мощности марины (количество мест).  Обрабатываем возможные отсутствия ключей.
            water_capacity = marina.get('capacity:water', None)  # Количество мест на воде
            land_capacity = marina.get('capacity:land', None)    # Количество мест на суше

            # Собираем данные для текущей марины
            marina_info = {
                'city': city_name,
                'marina_number': i + 1,  # Нумерация с 1
                'latitude': lat,
                'longitude': lon,
                'water_capacity': water_capacity,
                'land_capacity': land_capacity
            }
            marina_data.append(marina_info)

        # 5. Создаем DataFrame из списка данных о маринах
        df = pd.DataFrame(marina_data)

        # 6. Сохраняем DataFrame в CSV файл
        df.to_csv(output_filename, index=False)

        print(f"Информация о маринах в городе {city_name} сохранена в файл: {output_filename}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")





if __name__ == '__main__':
    get_marina_details_and_save_to_csv()