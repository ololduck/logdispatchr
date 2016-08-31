# -*- coding:utf-8 -*-

import logging

logger = logging.getLogger(__name__)


class BaseOutput(object):
    """
    Base class for all outputs.

    :param filtr: a shell glob based filter for the keys to be parsed
    :type filtr: str
    """
    def __init__(self, filtr='*'):
        self.filtr = filtr

    def _match(self, key):
        i = 0
        while i < len(key):
            if self.filtr[i] == '*':
                return True
            if key[i] != self.filtr[i]:
                return False
            i = i + 1

    def accept(self, message):
        """
        Method to call when trying to dispatch a Message.

        :param message: A record we wish to send to this output
        :type message: Message

        .. seealso: :doc:`models`
        """
        if 'key' not in message.keys():
            logger.warning('got message without key! %s, discarding', message)
            return
        if self._match(message.get('key')):
            self._write_message(message)

    def _write_message(self, message):
        """
        This method effectively writes the message to the transmission medium.
        Should be overriden by children

        :param message: A record we wish to send to this output
        :type message: Message
        :raises: NotImplemented

        .. seealso: :doc:`models`
        """
        raise NotImplemented


class ConsolePrinter(BaseOutput):
    """
    Dumb and useless console message printer. Simply write the raw message on
    stdout.

    Yeah, you probably don't need it.
    """
    def _write_message(self, message):
        logger.debug('Writing %s to console', message)
        print(message)
