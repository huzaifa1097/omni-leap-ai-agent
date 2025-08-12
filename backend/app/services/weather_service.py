import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_current_weather(city: str) -> str:
    """Fetches the current weather for a given city from OpenWeatherMap."""
    if not API_KEY:
        return "Error: Weather API key is not configured."

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric" # Use Celsius
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        
        return f"The current weather in {city} is {temperature}°C with {weather_description}."
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error fetching weather: {http_err}"
    except Exception as e:
        return f"An error occurred fetching weather: {e}"