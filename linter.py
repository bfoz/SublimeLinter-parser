from SublimeLinter.lint import Linter

from .linters import python as linter_python
from .parsers.recursive_descent import RecursiveDescent

class SublimeLinterParser(Linter):
    cmd = None      # Tell SublimeLinter to call the run() method instead of running an external tool

    # Match all views
    defaults = {
        'selector': 'source.python'
    }

    def run(self, cmd, code):
        print("---- RUN ---- ")
        parser = RecursiveDescent(linter_python)
        tree = parser.parse(code)
        if tree is None:
            print("tree = None")
        print("---- END RUN ----")

def plugin_loaded():
    print("Loaded!")
