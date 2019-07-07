from SublimeLinter.lint import Linter  # or NodeLinter, PythonLinter, ComposerLinter, RubyLinter


class Parser(Linter):
    cmd = '__cmd__'
    regex = r''
    multiline = False
    defaults = {
        'selector': 'source.python'
    }
