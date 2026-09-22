"""Real-time outdoor training weather tool for TriCoach AI using Open-Meteo API."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict


def get_outdoor_training_weather(location: str) -> Dict[str, Any]:
    """Fetch current outdoor training weather conditions (temperature, wind speed, precipitation) for a given city or location.

    Args:
        location: Name of the city or location (e.g. 'Boulder', 'Kona', 'Austin', 'San Francisco').

    Returns:
        Dictionary containing location details, temperature (°F), wind speed (mph), humidity (%), and precipitation.
    """
    api_key = os.environ.get("OPEN_METEO_API_KEY")
    key_param = f"&apikey={api_key}" if api_key else ""

    try:
        encoded_loc = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1&language=en&format=json{key_param}"

        req = urllib.request.Request(
            geo_url, headers={"User-Agent": "TriCoachAI/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            geo_data = json.loads(resp.read().decode())

        if not geo_data.get("results"):
            return {"error": f"Location '{location}' not found."}

        place = geo_data["results"][0]
        lat, lon = place["latitude"], place["longitude"]
        city_name = place.get("name", location)
        country = place.get("country", "")

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
            f"&temperature_unit=fahrenheit&wind_speed_unit=mph{key_param}"
        )

        w_req = urllib.request.Request(
            weather_url, headers={"User-Agent": "TriCoachAI/1.0"}
        )
        with urllib.request.urlopen(w_req, timeout=10) as w_resp:
            w_data = json.loads(w_resp.read().decode()).get("current", {})

        return {
            "location": f"{city_name}, {country}".strip(", "),
            "temperature_fahrenheit": w_data.get("temperature_2m"),
            "wind_speed_mph": w_data.get("wind_speed_10m"),
            "humidity_percent": w_data.get("relative_humidity_2m"),
            "precipitation_inches": w_data.get("precipitation"),
            "training_conditions_summary": (
                f"Conditions in {city_name}: {w_data.get('temperature_2m')}°F, "
                f"Wind: {w_data.get('wind_speed_10m')} mph, "
                f"Humidity: {w_data.get('relative_humidity_2m')}%, "
                f"Precipitation: {w_data.get('precipitation')} in."
            ),
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch weather data for '{location}': {str(e)}"
        }
