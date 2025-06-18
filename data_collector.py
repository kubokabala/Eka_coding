import osmnx as ox
import pandas as pd
from click import progressbar
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic
from tqdm import tqdm

def get_nearby_amenities_geopy(lat, lon, distance=1000):
    """
    Находит количество продуктовых магазинов, культурных достопримечательностей и отелей
    в заданном радиусе от заданных координат с использованием geopy и ArcGIS.

    Args:
        lat (float): Широта.
        lon (float): Долгота.
        distance (int, optional): Радиус поиска в метрах. Defaults to 1000.

    Returns:
        dict: Словарь с количеством ближайших продуктовых магазинов, достопримечательностей и отелей.
    """
    try:
        geolocator = ArcGIS()

        # Определяем типы мест для поиска (адаптируем под geopy/ArcGIS)
        amenities = {
            "grocery": "Grocery Store",  # Пример, может потребоваться адаптация
            "culture": "Museum",       # Пример, может потребоваться адаптация
            "hotel": "Hotel"            # Пример, может потребоваться адаптация
        }

        nearby_counts = {}

        for amenity_type, query in amenities.items():
            nearby_count = 0
            location = geolocator.reverse((lat, lon)) # Обратное геокодирование для получения адреса
            if location:
                search_string = f"{query} near {location.address}" #Формируем строку поиска
                places = geolocator.geocode(search_string, exactly_one=False) # Ищем места

                if places:
                  for place in places:
                    if geodesic((lat, lon), (place.latitude, place.longitude)).meters <= distance:
                      nearby_count += 1
                nearby_counts[amenity_type] = nearby_count
            else:
                nearby_counts[amenity_type] = None # Если не удалось определить местоположение
        return nearby_counts

    except Exception as e:
        print(f"Произошла ошибка при поиске ближайших объектов: {e}")
        return {"grocery": None, "culture": None, "hotel": None}

def get_marina_details_and_save_to_csv(city_name="Санкт-Петербург", output_filename="marinas_detailed.csv"):
    """
    Извлекает подробную информацию о маринах из OpenStreetMap и ArcGIS (через geopy) для заданного города,
    включая количество ближайших продуктовых магазинов, культурных достопримечательностей и отелей.
    Сохраняет результат в CSV файл, где каждая строка соответствует одной марине.
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
        for i, (index, marina) in tqdm(enumerate(marinas.iterrows())):
            # Получаем координаты (центроид геометрии)
            if marina['geometry'].geom_type == 'Polygon':
                lon = marina['geometry'].centroid.x
                lat = marina['geometry'].centroid.y
            elif marina['geometry'].geom_type == 'Point':
                lon = marina['geometry'].x
                lat = marina['geometry'].y
            else:
                lon = None
                lat = None

            # 5. Получаем информацию о ближайших объектах (используем geopy/ArcGIS)
            nearby_amenities = get_nearby_amenities_geopy(lat, lon)

            # 6. Извлекаем информацию о мощности марины (количество мест)
            water_capacity = marina.get('capacity:water', None)
            land_capacity = marina.get('capacity:land', None)

            # 7. Собираем данные для текущей марины
            marina_info = {
                'city': city_name,
                'marina_number': i + 1,
                'latitude': lat,
                'longitude': lon,
                'water_capacity': water_capacity,
                'land_capacity': land_capacity,
                'nearby_grocery_stores': nearby_amenities.get('grocery', None),
                'nearby_cultural_attractions': nearby_amenities.get('culture', None),
                'nearby_hotels': nearby_amenities.get('hotel', None)
            }
            marina_data.append(marina_info)

        # 8. Создаем DataFrame из списка данных о маринах
        df = pd.DataFrame(marina_data)

        # 9. Сохраняем DataFrame в CSV файл
        df.to_csv(output_filename, index=False)

        print(f"Информация о маринах в городе {city_name} сохранена в файл: {output_filename}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    get_marina_details_and_save_to_csv()