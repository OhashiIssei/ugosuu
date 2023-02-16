import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

def print_json(JSON):
    data = json.dumps(JSON, indent=1,ensure_ascii=False)
    print(highlight(data, JsonLexer(), TerminalFormatter()))