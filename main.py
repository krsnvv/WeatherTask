import json
from collections import defaultdict
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass
class WeatherData:
    city: str
    temperature: int
    country: str


def load_cities(filename: str) -> list[str]:
    with open(filename, "r", encoding="utf-8") as file:
        return [
            line.strip()
            for line in file
            if line.strip()
        ]


def get_weather(city: str) -> WeatherData:
    city_encoded = quote(city)

    url = f"https://wttr.in/{city_encoded}?format=j1"

    request = Request(
        url,
        headers={
            "User-Agent": "WeatherTask"
        }
    )

    try:
        with urlopen(request, timeout=15) as response:
            data = json.load(response)

    except HTTPError as error:
        raise RuntimeError(
            f"HTTP ошибка для {city}: {error.code}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"Ошибка соединения для {city}: {error.reason}"
        ) from error

    current_condition = data["current_condition"][0]
    nearest_area = data["nearest_area"][0]

    temperature = int(
        current_condition["temp_C"]
    )

    country = (
        nearest_area["country"][0]["value"]
    )

    return WeatherData(
        city=city,
        temperature=temperature,
        country=country,
    )


def print_weather(
    weather_data: list[WeatherData]
) -> None:
    print()
    print("Погода по городам:")
    print()

    for item in weather_data:
        temperature = f"{item.temperature:+d}"

        print(
            f"{item.city}, "
            f"{item.country} "
            f"{temperature} °C"
        )


def print_country_statistics(
    weather_data: list[WeatherData]
) -> None:
    grouped = defaultdict(list)

    for item in weather_data:
        grouped[item.country].append(
            item.temperature
        )

    print()
    print("Статистика по странам:")
    print()

    for country, temperatures in sorted(
        grouped.items()
    ):
        city_count = len(temperatures)

        average_temperature = (
            sum(temperatures) / city_count
        )

        minimum_temperature = min(
            temperatures
        )

        maximum_temperature = max(
            temperatures
        )

        print(
            f"{country} — "
            f"{city_count} cities, "
            f"avg: {average_temperature:+.1f} °C, "
            f"min: {minimum_temperature:+d} °C, "
            f"max: {maximum_temperature:+d} °C"
        )


def main() -> None:
    cities = load_cities("cities.txt")

    weather_data = []

    for city in cities:
        print(
            f"Получаю данные для {city}..."
        )

        try:
            weather = get_weather(city)

            weather_data.append(
                weather
            )

        except RuntimeError as error:
            print(error)

    print_weather(weather_data)

    print_country_statistics(
        weather_data
    )


if __name__ == "__main__":
    main()