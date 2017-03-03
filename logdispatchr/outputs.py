# -*- coding:utf-8 -*-

import socket
import msgpack
import logging

from logdispatchr.models import InvalidMessageError, Message
from logdispatchr.formatters import get_formatter

logger = logging.getLogger(__name__)


class BaseOutput(object):
    """
    Base class for all outputs.

    :param filtr: a shell glob based filter for the keys to be parsed
    :type filtr: str
    :default filtr: *
    :param formatter: The name of a formatter to use when we write the message,
                      as `logdispatchr.formatters.get_formatter` would use.
    :type formatter: str
    :default formatter: dumb

    .. seealso: :doc:`formatters.get_formatter`
    """
    def __init__(self, filtr='*', formatter='dumb'):
        self.filtr = filtr
        self.formatter = get_formatter(formatter)

    def _match(self, key: str):
        """
        Internal fuction checking if the recieved key matches the set filter

        :example:
        >>> out = BaseOutput('hello.*')
        >>> out._match('hi')
        False
        >>> out._match('hello')
        False
        >>> out._match('hello.')
        True
        >>> out._match('hello.world')
        True
        >>> out._match(999)
        Traceback (most recent call last):
            ...
        logdispatchr.models.InvalidMessageError: key is not a string! (is: <class 'int'>)
        """
        if type(key) != str:
            raise InvalidMessageError('key is not a string! \
(is: {})'.format(type(key)))
        i = 0
        while i < len(key) or i < len(self.filtr) and self.filtr[i] != '*':
            if i >= len(key):
                return False
            if self.filtr[i] == '*':
                return True
            if key[i] != self.filtr[i]:
                return False
            i = i + 1
        return True

    def accept(self, message: Message) -> bool:
        """
        Method to call when trying to dispatch a Message.

        :param message: A record we wish to send to this output
        :type message: Message

        .. seealso: :doc:`models`

        :example:
        >>> class DumbOutput(BaseOutput):
        ...     # needed, as BaseOutput._write_message
        ...     # will throw NotImplementedError
        ...     def _write_message(self, message):
        ...         pass
        ...
        >>> output = DumbOutput(filtr='myfilter')
        >>> bad = {'key': 'badfilter', 'message': 'I love you!'}
        >>> nope = {'message': 'hi!', 'other': 'other_value'}
        >>> good = {'key': 'myfilter', 'message': 'hello!'}
        >>> output.accept(bad)
        False
        >>> output.accept(nope)
        False
        >>> output.accept(good)
        True
        """
        if 'key' not in message.keys():
            logger.warning('got message without key! %s, discarding', message)
            return False
        try:
            if self._match(message.get('key')):
                self._write_message(message)
                return True
        except InvalidMessageError as e:
            logger.exception("Got an invalid message", e)
        return False

    def _write_message(self, message: Message):
        """
        This method effectively writes the message to the transmission medium.
        Should be overriden by children

        Please note that children should also call
        `self.formatter.format(message)`.

        :param message: A record we wish to send to this output
        :type message: Message
        :raises: NotImplemented

        .. seealso: :doc:`models`
        """
        raise NotImplementedError("please override _write_message")


class ConsolePrinter(BaseOutput):
    """
    Dumb and useless console message printer. Simply write the raw message on
    stdout.

    Yeah, you probably don't need it.

    :example:
    >>> out = ConsolePrinter()
    >>> msg = {'key': 'test', 'message': 'hello, world'}
    >>> out.accept(msg)
    {'key': 'test', 'message': 'hello, world'}
    True
    """
    def _write_message(self, message: Message):
        logger.debug('Writing %s to console', message)
        print(self.formatter.format(message))


class LogdispatchrForwarder(BaseOutput):
    """
    Forwards message to an other logdispatchr instance, using UDP.

    :param target_host: Where to forward the messages
    :type target_host: str
    :param target_port: port le reciever instance is listening to
    :type target_port: int
    """
    def __init__(self, **kwargs):
        self.host = kwargs.pop('target_host')
        self.port = kwargs.pop('target_port', 5140)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        kwargs.pop('formatter', 'lets get rid of that')
        super().__init__(**kwargs)

    def _write_message(self, message: Message):
        self.sock.sendto(msgpack.packb(message),
                         (self.host, self.port))


class FileOutput(BaseOutput):
    """
    Write the recieved messages into a file

    :param path: where we should write to. please ensure the correct
                 permissions to do this
    :type path: str
    :example:
    >>> out = FileOutput(path='/tmp/pytest')
    >>> msg = {'key': 'test', 'message': 'hello, world'}
    >>> out.accept(msg)
    True
    >>> out.fp.flush() # mandatory for the test
    >>> with open('/tmp/pytest', 'r') as f:
    ...     print(f.read())
    ...
    {'key': 'test', 'message': 'hello, world'}
    >>> import os # let's clean up after ourselves
    >>> os.remove('/tmp/pytest')
    """
    def __init__(self, **kwargs):
        self.path = kwargs.pop('path')
        self.fp = open(self.path, 'a+')
        super().__init__(**kwargs)

    def _write_message(self, message: Message):
        if self.fp.write(self.formatter.format(message)) != \
                len(self.formatter.format(message)):
            logger.error('Could not fully write to {}, please investigate',
                         self.path)
