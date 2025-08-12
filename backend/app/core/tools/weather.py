from langchain.tools import tool
from app.services.weather_service import get_current_weather

@tool
def weather_tool(city: str) -> str:
    """
    Use this tool to get the current weather for a specific city.
    For example, ask 'what is the weather in London?'.
    """
    return get_current_weather(city)