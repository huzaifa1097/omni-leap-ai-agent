import os
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException # Import the specific exception
from langchain.tools import tool

@tool
def news_tool(query: str) -> str:
    """
    Use this tool to get the latest news headlines on a specific topic.
    For example: 'what is the latest news on artificial intelligence?'
    """
    try:
        newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        
        # FIX: Use get_everything() for better results on general topics.
        all_articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=5
        )
        
        if all_articles['totalResults'] == 0:
            return f"I couldn't find any recent news articles for '{query}'."
        
        articles = all_articles['articles']
        result = f"Here are the top {len(articles)} news articles for '{query}':\n"
        for article in articles:
            # Also include the source for better context
            result += f"- {article['title']} (Source: {article['source']['name']})\n"
        
        return result
    
    # FIX: More specific error handling to reveal the real problem.
    except NewsAPIException as e:
        # This will show us if the API key is wrong or if there's another API issue.
        return f"An error occurred with the News API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"