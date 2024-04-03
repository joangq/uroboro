import textwrap

from lark import Lark
from lark.indenter import Indenter
import os.path

from datetime import datetime
import pytz

class staticproperty(property):
    """Utilidad para crear propiedades estáticas (que no tomen el puntero a self)"""

    def __get__(self, cls, owner):
        return staticmethod(self.fget).__get__(None, owner)()
    
def parse_time(time_string, timezone=None):
    original_datetime = datetime.fromisoformat(time_string.replace("Z", "+00:00"))
    if not timezone:
        return original_datetime
    
    timezone = pytz.timezone(timezone)
    return original_datetime.astimezone(timezone)

def parse_timex(timezone):
    return lambda time_string: parse_time(time_string, timezone=timezone)

parse_time_arg = parse_timex('America/Argentina/Buenos_Aires')

def format_time(time_object, format):
    return time_object.strftime(format)

def format_timex(format):
    return lambda time_object: format_time(time_object, format)

timeformat = format_timex("%d/%m/%y %H:%M:%S")

class now:
    # noinspection PyMethodParameters
    @staticproperty
    def string():
        return timeformat(datetime.now())

class PythonIndenter(Indenter):
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

with open('grammar.lark', 'r') as file:
    grammar = file.read()

_lark_grammar = None

def parse(code, dedent=False, pretty=True):
    global _lark_grammar
    if dedent:
        code = textwrap.dedent(code)
    out = _lark_grammar.parse(code + "\n")

    if pretty:
        return out.pretty(indent_str='    ')
    return out

program_path = 'program.xyz'
folder, file = os.path.split(program_path)
file, ext = os.path.splitext(file)
outfile = os.path.join(folder, file + '.ast')

with open(program_path, 'r') as src:
    program = src.read()

try:
    _lark_grammar = Lark(
        grammar,
        parser="lalr",
        start="module",
        postlex=PythonIndenter(),
    )

    out_str = str(parse(program))
except Exception as ex:
    out_str = str(ex)

with open(outfile, 'w') as out:
    now_str = now.string
    out_str = f"<< Generated at {now_str} >>\n\n" + out_str
    out.write(out_str)