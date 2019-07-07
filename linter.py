from SublimeLinter.lint import Linter

class SublimeLinterParser(Linter):
    cmd = None 		# Tell SublimeLinter to call the run() method instead of running an external tool

    # Match all views
    defaults = {
        'selector': 'source.python'
    }

    def run(self, cmd, code):
    	print("---- RUN ---- ")
    	# print(code)
    	print("---- END RUN ----")

def plugin_loaded():
    print("Loaded!")
