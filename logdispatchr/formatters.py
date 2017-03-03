# -*- coding:utf-8 -*-

from logdispatchr.models import InvalidConfigurationError


def get_formatter(formatter: str):
    from logdispatchr.core import CURRENT_CONFIG
    if formatter == 'dumb':
        return Dumbformatter()
    if formatter == 'raw_message':
        return RawMessageFormatter()
    if not CURRENT_CONFIG:
        raise InvalidConfigurationError('could not find formatter {}',
                                        formatter)
    formatter_list = CURRENT_CONFIG.get_declared_formatters()
    for e in formatter_list:
        if e.uid == formatter:
            return e
    raise InvalidConfigurationError('could not find formatter {}',
                                    formatter)


class BaseFormatter(object):
    def __init__(self, format_string: str, uid: str):
        self.format_string = format_string
        self.uid = uid

    def format(self, **data) -> str:
        return self.format_string.format(**data)


class RawMessageFormatter(BaseFormatter):
    """
    Just returns the message part.

    :example:
    >>> f = RawMessageFormatter()
    >>> message = {'key': 'test', 'message': 'hello'}
    >>> f.format(**message)
    'hello\n'
    """
    def __init__(self, uid='raw_message'):
        super().__init__('{message}\n', uid)


class Dumbformatter(BaseFormatter):
    def __init__(self):
        self.format = dict.__str__
