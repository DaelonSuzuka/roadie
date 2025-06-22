import logging
from logging.config import dictConfig
from uuid import uuid4


DEVELOPMENT = True
try:
    from .settings import Settings

    DEVELOPMENT = Settings().DEVELOPMENT
except ImportError:
    pass


class Tagger:
    tags: list[str] = []

    def __init__(self, tag: str = '', **kwargs: str) -> None:
        if tag == 'job':
            tag += '=' + uuid4().hex[:6]
        self.tag = tag

        self.kwargs = kwargs

    def __enter__(self, *_):
        if self.tag:
            Tagger.tags.append(self.tag)

        for k, v in self.kwargs.items():
            Tagger.tags.append(f'{k}={v}')

        return self

    def __exit__(self, *_):
        if self.tag:
            Tagger.tags.remove(self.tag)

        for k, v in self.kwargs.items():
            Tagger.tags.remove(f'{k}={v}')


# --------------------------------------------------------------------------- #


class C:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    OFF = '\033[0m'

    if DEVELOPMENT:

        @classmethod
        def dim(cls, text: str):
            return C.DIM + text + C.OFF

        @classmethod
        def apply(cls, text: str, style: str | list[str]):
            if isinstance(style, list):
                style = ''.join(style)
            return style + text + C.OFF
    else:

        @classmethod
        def dim(cls, text: str):
            return text

        @classmethod
        def apply(cls, text: str, style: str | list[str]):
            return text


class CustomFormatter(logging.Formatter):
    _time = C.dim('%(asctime)s ')
    _meta = C.dim(' %(name)s') + ' %(tags)s' + C.dim('(%(filename)s:%(lineno)d) ')

    FORMATS = {
        10: _time + C.apply('[DEBUG   ]', C.BLUE) + _meta + '%(message)s',
        20: _time + C.apply('[INFO    ]', C.GREEN) + _meta + '%(message)s',
        30: _time + C.apply('[WARNING ]', C.YELLOW) + _meta + '%(message)s',
        40: _time + C.apply('[ERROR   ]', C.RED) + _meta + '%(message)s',
        50: _time + C.apply('[CRITICAL]', C.MAGENTA) + _meta + '%(message)s',
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, '')
        formatter = logging.Formatter(log_fmt)

        record.tags = f'[{", ".join(Tagger.tags)}] ' if Tagger.tags else ''
        return formatter.format(record)


DEFAULT_LOGGER = 'roadie'

config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': CustomFormatter,
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        DEFAULT_LOGGER: {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

dictConfig(config)


# *************************************************************************** #


class Log(logging.Logger):
    _loggers: dict[str, logging.Logger] = {}

    def __init__(self) -> None:
        self._logger = self.__call__()

    def __getattr__(self, name: str):
        return self._logger.__getattribute__(name)

    def __call__(self, name=DEFAULT_LOGGER) -> logging.Logger:
        name = name.removeprefix(f'{DEFAULT_LOGGER}.')
        if name == '':
            name = DEFAULT_LOGGER
        if name != DEFAULT_LOGGER:
            name = f'{DEFAULT_LOGGER}.' + name

        if name not in Log._loggers:
            Log._loggers[name] = logging.getLogger(name)

        return Log._loggers[name]

    def tag(self, tag: str):
        def decorator(wrapped):
            def wrapper(*args, **kwargs):
                with Tagger(tag):
                    return wrapped(*args, **kwargs)

            return wrapper

        return decorator

    def trace(self):
        pass


log = Log()


# *************************************************************************** #


if __name__ == '__main__':
    log.debug('debug')
    log.info('info')
    log.warning('warning')
    log.error('error')
    log.critical('critical')

    print('-' * 100)

    lg = log('named_logger')
    lg.debug('debug')
    lg.info('info')
    lg.warning('warning')
    lg.error('error')
    lg.critical('critical')

    print('-' * 100)

    with Tagger('with_tag'):
        log.debug('debug')
        log.info('info')
        with Tagger('and'):
            log.warning('warning')
            log.error('error')
            with Tagger('more_tags'):
                log.critical('critical')

    print('-' * 100)

    @log.tag('inner')
    def inner():
        log.info('test')

    @log.tag('outer')
    def outer():
        log.debug('before')
        inner()

        log.debug('after')

    log.debug('start')
    outer()
    log.debug('end')

    print('-' * 100)

    with Tagger('job'):
        log.info('nested job ID')
        with Tagger('job'):
            log.info('')
        log.info('')

    print('-' * 100)

    with Tagger(keyword='tags', comma='multiple'):
        log.debug('')
        with Tagger('regular tag'):
            log.info('')
            with Tagger(more='keywords'):
                log.info('')
        log.debug('')
