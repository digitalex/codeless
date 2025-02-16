def wrap_code_in_markdown(code: str, language: str = 'python') -> str:
    return f'```{language}\n{code}\n```\n\n'


def extract_code(content: str, language: str = 'python') -> str:
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
