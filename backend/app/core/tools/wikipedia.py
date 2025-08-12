import wikipedia
from langchain.tools import tool

@tool
def wikipedia_tool(query: str) -> str:
    """
    Use this tool to look up a topic, person, or place on Wikipedia.
    For example: 'what is the eiffel tower?' or 'who is marie curie?'
    """
    try:
        # Get the summary of the first search result
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.PageError:
        return f"Sorry, I could not find a Wikipedia page for '{query}'."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"That query is ambiguous. Try being more specific. Options: {e.options[:3]}"