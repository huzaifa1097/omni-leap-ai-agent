import os
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

def get_available_search_tools():
    """
    Get available search tools based on what's installed and configured.
    """
    tools = []
    
    # Option 1: Try DuckDuckGoSearchTool (no API key needed)
    try:
        from crewai_tools import DuckDuckGoSearchTool
        duckduckgo_tool = DuckDuckGoSearchTool()
        tools.append(duckduckgo_tool)
        print("✓ Added DuckDuckGoSearchTool")
    except ImportError:
        print("✓ DuckDuckGoSearchTool available")

    # Option 2: Try SerperDevTool if API key is available
    try:
        from crewai_tools import SerperDevTool
        if os.getenv("SERPER_API_KEY"):
            serper_tool = SerperDevTool()
            tools.append(serper_tool)
            print("✓ Added SerperDevTool (requires SERPER_API_KEY)")
        else:
            print("⚠ SerperDevTool available but SERPER_API_KEY not set")
    except ImportError:
        print("✗ SerperDevTool not available")
    
    # Option 3: Add ScrapeWebsiteTool as backup
    try:
        from crewai_tools import ScrapeWebsiteTool
        scrape_tool = ScrapeWebsiteTool()
        tools.append(scrape_tool)
        print("✓ Added ScrapeWebsiteTool")
    except ImportError:
        print("✗ ScrapeWebsiteTool not available")
    
    return tools

def get_groq_llm():
    """
    Initialize Groq LLM using CrewAI's native LLM wrapper
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise Exception("""
        ❌ GROQ_API_KEY not found! 
        
        Get your free API key from: https://console.groq.com/
        Then add to your .env file: GROQ_API_KEY=your_key_here
        """)
    
    try:
        # Use CrewAI's native LLM wrapper for better compatibility
        # Using Llama 3.3 70B - the most capable current production model
        llm = LLM(
            model="groq/llama-3.3-70b-versatile",  # Current production model
            api_key=groq_api_key,
            temperature=0.7
        )
        print("✅ Using Groq (Llama 3.3 70B) via CrewAI LLM wrapper - Free tier: 30 requests/minute")
        return llm
        
    except Exception as e:
        raise Exception(f"❌ Failed to initialize Groq: {str(e)}")

# Get available tools and LLM
available_tools = get_available_search_tools()
llm = get_groq_llm()

# Define agents
researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover groundbreaking technologies and trends on a given topic using available research tools.',
    backstory="""You are a world-class research analyst for a leading tech magazine. 
    You have deep expertise in emerging technologies, market trends, and industry analysis. 
    You are skilled at using various research tools to gather comprehensive information.""",
    verbose=True,
    allow_delegation=False,
    tools=available_tools,
    llm=llm
)

writer = Agent(
    role='Tech Content Strategist', 
    goal='Craft compelling content on technical advancements.',
    backstory="""You are a renowned content strategist, known for writing engaging and 
    insightful articles about technology. You excel at transforming research 
    data into compelling narratives.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

def create_blog_post_crew(topic: str):
    """
    Creates and executes a blog post crew for the given topic.
    """
    print(f"🚀 Creating blog post crew for topic: {topic}")
    
    # Research task
    task_research = Task(
        description=f"""Conduct comprehensive research on '{topic}' for a tech blog article.
        Focus on the latest developments, key players, challenges, and future outlook.
        Use available search tools to gather current information.""",
        expected_output=f"""A comprehensive research report on '{topic}' with clear sections
        covering the current landscape, key players, technical details, challenges, and future predictions.
        Include sources where possible.""",
        agent=researcher
    )
    
    # Writing task  
    task_write = Task(
        description=f"""Transform the research report into an engaging, professional blog post about '{topic}'.
        The article should have a compelling headline, an engaging introduction, well-structured sections,
        and a strong conclusion. The tone should be authoritative yet accessible.
        Format the output in markdown with proper headings, bullet points where appropriate.""",
        expected_output=f"""A complete, publication-ready blog post about '{topic}' in markdown format,
        between 1200-1600 words with proper structure:
        - Compelling headline
        - Executive summary
        - Introduction
        - Main content sections with subheadings
        - Conclusion
        - Key takeaways""",
        agent=writer
    )
    
    # Create crew
    blog_crew = Crew(
        agents=[researcher, writer],
        tasks=[task_research, task_write],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute crew
    try:
        print("🔍 Starting research and writing process...")
        result = blog_crew.kickoff()
        print("✅ Blog post creation completed successfully!")
        return str(result)
        
    except Exception as e:
        error_msg = f"❌ Error executing blog crew: {str(e)}"
        print(error_msg)
        return f"I apologize, but my AI crew is a bit overwhelmed at the moment. This can happen with very broad or complex topics that require a lot of research. Please try your request again in a few moments, or try a more specific topic."

# Example usage
if __name__ == "__main__":
    # Test the crew
    topic = "Artificial Intelligence in Healthcare"
    result = create_blog_post_crew(topic)
    print("\n" + "="*50)
    print("FINAL BLOG POST:")
    print("="*50)
    print(result)