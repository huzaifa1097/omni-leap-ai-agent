import os
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM


def _get_search_tools():
    tools = []
    try:
        from crewai_tools import DuckDuckGoSearchTool
        tools.append(DuckDuckGoSearchTool())
    except ImportError:
        pass

    try:
        from crewai_tools import SerperDevTool
        if os.getenv("SERPER_API_KEY"):
            tools.append(SerperDevTool())
    except ImportError:
        pass

    try:
        from crewai_tools import ScrapeWebsiteTool
        tools.append(ScrapeWebsiteTool())
    except ImportError:
        pass

    return tools


def _get_groq_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise Exception("GROQ_API_KEY not found in environment.")
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7,
    )


def create_blog_post_crew(topic: str) -> str:
    """Creates and executes a CrewAI blog post pipeline for the given topic."""
    print(f"Creating blog post crew for topic: {topic}")

    try:
        llm = _get_groq_llm()
    except Exception as e:
        return f"Cannot start blog crew: {e}"

    available_tools = _get_search_tools()

    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover groundbreaking technologies and trends on a given topic using available research tools.',
        backstory=(
            "You are a world-class research analyst for a leading tech magazine. "
            "You have deep expertise in emerging technologies, market trends, and industry analysis. "
            "You are skilled at using various research tools to gather comprehensive information."
        ),
        verbose=True,
        allow_delegation=False,
        tools=available_tools,
        llm=llm,
    )

    writer = Agent(
        role='Tech Content Strategist',
        goal='Craft compelling content on technical advancements.',
        backstory=(
            "You are a renowned content strategist, known for writing engaging and "
            "insightful articles about technology. You excel at transforming research "
            "data into compelling narratives."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    task_research = Task(
        description=(
            f"Conduct comprehensive research on '{topic}' for a tech blog article. "
            "Focus on the latest developments, key players, challenges, and future outlook. "
            "Use available search tools to gather current information."
        ),
        expected_output=(
            f"A comprehensive research report on '{topic}' with clear sections covering "
            "the current landscape, key players, technical details, challenges, and future predictions. "
            "Include sources where possible."
        ),
        agent=researcher,
    )

    task_write = Task(
        description=(
            f"Transform the research report into an engaging, professional blog post about '{topic}'. "
            "The article should have a compelling headline, an engaging introduction, well-structured sections, "
            "and a strong conclusion. The tone should be authoritative yet accessible. "
            "Format the output in markdown with proper headings, bullet points where appropriate."
        ),
        expected_output=(
            f"A complete, publication-ready blog post about '{topic}' in markdown format, "
            "between 1200-1600 words with proper structure:\n"
            "- Compelling headline\n- Executive summary\n- Introduction\n"
            "- Main content sections with subheadings\n- Conclusion\n- Key takeaways"
        ),
        agent=writer,
    )

    blog_crew = Crew(
        agents=[researcher, writer],
        tasks=[task_research, task_write],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = blog_crew.kickoff()
        print("Blog post creation completed successfully.")
        return str(result)
    except Exception as e:
        print(f"Error executing blog crew: {e}")
        return (
            "I apologize, but my AI crew is a bit overwhelmed at the moment. "
            "This can happen with very broad or complex topics that require a lot of research. "
            "Please try again in a few moments, or try a more specific topic."
        )
