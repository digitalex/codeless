def wrap_code_in_markdown(code: str, language: str = 'python') -> str:
    """Wraps a given code string in Markdown code fences.

    Args:
        code: The string containing the code to wrap.
        language: The language identifier for the Markdown code block (defaults to 'python').

    Returns:
        A string with the code wrapped in Markdown fences (```language ... ```).
    """
    return f'```{language}\n{code}\n```\n\n'


def extract_code(content: str, language: str = 'python') -> str:
    """Extracts the first code block for a given language from a string (e.g., Markdown).

    It looks for the first occurrence of ```language and extracts the content
    until the closing ```.

    Args:
        content: The string potentially containing the code block.
        language: The language identifier of the code block to extract (defaults to 'python').

    Returns:
        The extracted code as a string, or an empty string if no matching code block is found.
    """
    code_lines = []
    started = False
    for line in content.splitlines():
        if started:
            if line.strip() == '```':
                break
            else:
                code_lines.append(line.rstrip())
        elif line.strip() == f'```{language}':
            started = True

    return '\n'.join(code_lines)
