"""
Utility functions for agent operations.
"""

def wrap_code_in_markdown(code: str, language: str = 'python') -> str:
    """
    Wraps a code string in markdown code block.

    Args:
        code: The code string.
        language: The language for the markdown code block. Defaults to 'python'.

    Returns:
        The code string wrapped in markdown.
    """
    return f'```{language}\n{code}\n```\n\n'


def extract_code(content: str, language: str = 'python') -> str:
    """
    Extracts code from a markdown code block in a string.

    Args:
        content: The string containing the markdown code block.
        language: The language of the code block to extract. Defaults to 'python'.

    Returns:
        The extracted code as a string, or an empty string if not found.
    """
    code_lines = []
    started = False
    for line in content.splitlines():
        if started:
            if line.strip() == '```':
                break
            code_lines.append(line.rstrip()) # De-indented from else
        elif line.strip() == f'```{language}':
            started = True

    return '\n'.join(code_lines)
