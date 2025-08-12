from langchain_experimental.tools import PythonREPLTool
from langchain.agents import tool
import re

python_repl = PythonREPLTool()

def clean_python_code(code: str) -> str:
    """
    Helper function to robustly clean the Python code received from the LLM.
    It finds and extracts only the code inside a markdown block (```python...``` or ```...```),
    ignoring any conversational text before or after it.
    """
    # Remove any leading/trailing whitespace
    code = code.strip()
    
    # Use a regular expression to find the code block
    # Updated regex to handle both ```python and ``` blocks properly
    match = re.search(r"```(?:python\s*)?\n?(.*?)```", code, re.DOTALL | re.IGNORECASE)
    if match:
        # If a markdown block is found, extract the code from it
        cleaned_code = match.group(1).strip()
    else:
        # If no markdown block is found, assume the whole string is code
        cleaned_code = code
    
    # Remove any remaining explanatory text at the beginning
    lines = cleaned_code.split('\n')
    code_lines = []
    found_import_or_code = False
    
    for line in lines:
        line_stripped = line.strip()
        # Skip empty lines and comments until we find actual code
        if not line_stripped:
            if found_import_or_code:
                code_lines.append(line)
            continue
        if line_stripped.startswith('#'):
            if found_import_or_code:
                code_lines.append(line)
            continue
        # Check if this looks like explanatory text
        if not found_import_or_code and any([
            line_stripped.lower().startswith(('the ', 'here is', 'this ', 'please', 'i will', 'let me')),
            ':' in line_stripped and not any(keyword in line_stripped.lower() for keyword in ['import', 'def', 'class', 'if', 'for', 'while', 'try']),
            line_stripped.endswith(':') and not any(keyword in line_stripped.lower() for keyword in ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with'])
        ]):
            continue
        # This looks like actual code
        found_import_or_code = True
        code_lines.append(line)
    
    return '\n'.join(code_lines).strip()

@tool
def code_interpreter_tool(code: str) -> str:
    """
    Use this tool to execute Python code. The code should be a single, valid Python script.
    You can use it for calculations, data manipulation, or generating plots.
    When generating plots with matplotlib, you MUST save the plot to a file named 'static/plot.png'.
    The final line of your code MUST be a print statement of the result or the path to the saved plot.
    
    For example:
    `print(5**7)`
    or
    ```python
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3])
    plt.savefig('static/plot.png')
    print('static/plot.png')
    ```
    """
    try:
        # Clean the code before executing it
        cleaned_code = clean_python_code(code)
        
        # Additional validation - ensure we have actual code
        if not cleaned_code or cleaned_code.isspace():
            return "Error: No valid Python code found after cleaning."
        
        # Check if the cleaned code contains only explanatory text
        lines = [line.strip() for line in cleaned_code.split('\n') if line.strip()]
        if not lines:
            return "Error: No valid Python code found."
        
        # Execute the cleaned code
        result = python_repl.run(cleaned_code)
        return result
        
    except Exception as e:
        return f"Error executing code: {e}. Cleaned code was: {repr(cleaned_code)}"

# Example usage and test function
def test_code_cleaning():
    """Test function to verify the code cleaning works properly"""
    test_cases = [
        # Case 1: Code with markdown and explanation
        '''Please find the code below:
```python
import yfinance as yf
import matplotlib.pyplot as plt

tesla_data = yf.download('TSLA', start='2020-01-01', end='2022-02-26')
print("Data downloaded")
```''',
        
        # Case 2: Code with explanation but no markdown
        '''The provided code has a syntax error. Here is the corrected code:

import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3]})
print(df)''',
        
        # Case 3: Simple code block
        '''```
x = 5 + 3
print(x)
```''',
        
        # Case 4: Just plain code
        '''import numpy as np
arr = np.array([1, 2, 3])
print(arr.sum())'''
    ]
    
    for i, test_code in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("Original:", repr(test_code))
        cleaned = clean_python_code(test_code)
        print("Cleaned:", repr(cleaned))
        print("Cleaned code:\n", cleaned)

# Uncomment the line below to run tests
# test_code_cleaning()