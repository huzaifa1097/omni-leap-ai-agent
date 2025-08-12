#!/usr/bin/env python3
"""
Debug script to check what CrewAI tools are available
"""

print("=== Checking CrewAI Tools Availability ===\n")

# Check crewai_tools package
try:
    import crewai_tools
    print("✓ crewai_tools package imported successfully")
    print("Available attributes:", [attr for attr in dir(crewai_tools) if not attr.startswith('_')])
    print()
except ImportError as e:
    print(f"✗ Failed to import crewai_tools: {e}\n")

# Test specific tool imports
tools_to_test = [
    "DuckDuckGoSearchRun",
    "DuckDuckGoSearchTool", 
    "SerperDevTool",
    "ScrapeWebsiteTool",
    "WebsiteSearchTool"
]

for tool_name in tools_to_test:
    try:
        tool_class = getattr(crewai_tools, tool_name)
        print(f"✓ {tool_name}: Available")
    except (ImportError, AttributeError) as e:
        print(f"✗ {tool_name}: Not available ({e})")

print("\n=== Checking Alternative Options ===\n")

# Check langchain community tools
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    print("✓ DuckDuckGoSearchRun from langchain_community: Available")
except ImportError as e:
    print(f"✗ DuckDuckGoSearchRun from langchain_community: Not available ({e})")

# Check duckduckgo-search
try:
    from duckduckgo_search import DDGS
    print("✓ duckduckgo-search package: Available")
except ImportError as e:
    print(f"✗ duckduckgo-search package: Not available ({e})")

print("\n=== Package Versions ===\n")

packages_to_check = ['crewai', 'crewai_tools', 'langchain', 'langchain_community']
for package in packages_to_check:
    try:
        import importlib.metadata
        version = importlib.metadata.version(package)
        print(f"{package}: {version}")
    except Exception as e:
        print(f"{package}: Version not found ({e})")

print("\n=== Recommendations ===\n")
print("If tools are missing, try:")
print("1. pip install --upgrade crewai crewai-tools")
print("2. pip install langchain-community")
print("3. pip install duckduckgo-search")
print("4. Check if you need to restart your Python environment")