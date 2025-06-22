from utils import singleton, log
from abc import ABC


class SandboxExtension(ABC):
    name: str | list[str]


@singleton
class Sandbox:
    extensions: dict[str, SandboxExtension] = {}

    def __init__(self):
        self.this = None
        self.source = None

        # register all extensions
        for ext in SandboxExtension.__subclasses__():
            e = ext()
            if isinstance(ext.name, list):
                for name in ext.name:
                    self.extensions[name] = e
            else:
                self.extensions[ext.name] = e

        self.reset_environment()

    def __getattr__(self, name: str):
        return self.extensions[name]

    def __getitem__(self, name: str):
        return self.extensions[name]

    def _save(self, name: str, value):
        self._data[name] = value

    def _load(self, name: str):
        return self._data[name]

    def _print(self, *args):
        log.debug(*args)

    def reset_environment(self):
        self._data = {}
        self._globals = {
            'save': self._save,
            'load': self._load,
            'data': self._data,
            'print': self._print,
            'this': self.this,
            'source': self.source,
            **self.extensions,
        }
        self._locals = {}

    def compile(self, text, error_cb=None):
        error = ''
        try:
            compile(text, '', 'exec')
        except Exception as e:
            error = str(e)

        if error_cb:
            error_cb(error)

    def run(self, text, error_cb=None):
        if text == '':
            log.warning("can't exec an empty string!")
            return

        error = ''
        try:
            code = compile(text, '', 'exec')
            self._globals['this'] = self.this
            self._globals['source'] = self.source
            exec(code, self._globals, self._locals)
        except Exception as e:
            error = str(e)
            if error_cb:
                error_cb(error)
            else:
                log.error(error)
        finally:
            self._globals['this'] = None
            self._globals['source'] = None

    def eval(self, text, error_cb=None):
        if text == '':
            log.warning("can't exec an empty string!")
            return

        error = ''
        try:
            code = compile(text, '', 'eval')
            self._globals['this'] = self.this
            self._globals['source'] = self.source
            eval(code, self._globals, self._locals)
        except Exception as e:
            error = str(e)
            if error_cb:
                error_cb(error)
            else:
                log.error(error)
        finally:
            self._globals['this'] = None
            self._globals['source'] = None


if __name__ == '__main__':
    log.info('lol')

    class TestExtension(SandboxExtension):
        name = ['test', 't']

    class OtherExtension(SandboxExtension):
        name = 'other'

    sb = Sandbox()

    log.info(sb.extensions.keys())

    sb.run('print(this)')
    sb.run('')
    sb.run('print(test)')
    sb.run('print(test.name)')

    sb.run('save("data", "penis")')
    sb.run('print(load("data"))')