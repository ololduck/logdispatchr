# -*- coding:utf-8 -*-

import queue
import logging
import msgpack
import threading
import socketserver


from logdispatchr import formatters
from logdispatchr.models import Message

logger = logging.getLogger(__name__)


class BaseInput(object):
    """
    This class takes stuff from a source, and converts it in the standard
    internal message format. It is also the base class for any input.

    :param formatter: A string identifying the formatter to use
    :param key: the identifier for the messages comming from this source
    :param max_waiting_messages: the size of the internal queue.
    :type formatter: str
    :type key: str
    :type max_waiting_messages: queue.Queue
    """
    def __init__(self, **kwargs):
        self.formatter = formatters.get_formatter(
                kwargs.get('formatter', None))
        self.key = kwargs.get('key', 'undefined')
        self.messages = queue.Queue(kwargs.get('max_waiting_messages', 10))

    def setup(self):
        """
        Any operation needed before actually recieving messages. Should be
        overriden in child classes if needed.
        """
        pass

    # rewrite this as iterators?
    def has_available_message(self):
        """
        :rtype: boolean
        :return: wether we have messages waiting or not.
        """
        return self.messages.qsize() > 0

    def get(self):
        """
        :return: the next message in the queue
        :rtype: Message

        .. seealso:: :doc:`models`
        """
        return self.messages.get()


class UDPSyslogInput(BaseInput):
    """
    A naïve UDP rsyslog reciever. Doesn't parse the recieved message.

    :param host: the host to bind to. The most common is 0.0.0.0, to listen to
                 all interfaces, but localhost or 127.0.0.1 are a possibility
    :type host: str
    :param port: the port we should listen to
    :type port: int
    """

    class UDPSyslogServer(socketserver.UDPServer):
        def __init__(self, host, port, message_queue, key):
            self.message_queue = message_queue
            self.key = key
            super().__init__((host, port), UDPSyslogInput.UDPSyslogHandler)

    class UDPSyslogHandler(socketserver.DatagramRequestHandler):
        def handle(self):
            data = bytes.decode(self.request[0].strip())
#            socket = self.request[1]
            m = Message()
            m['message'] = str(data)
            m['key'] = self.server.key
            logger.debug('got UDP syslog message: %s from %s',
                         m, self.client_address[0])
            self.server.message_queue.put(m)

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 514)
        super().__init__(**kwargs)
        self.setup()

    def setup(self):
        self.server = UDPSyslogInput.UDPSyslogServer(self.host, self.port,
                                                     self.messages, self.key)
        self.serverthread = threading.Thread(target=self.server.serve_forever)
        self.serverthread.setDaemon(True)
        self.serverthread.start()
        logger.info("successfully started Rsyslog server on %s:%s",
                    self.host, self.port)


class LogdispatchrUDPInput(BaseInput):
    """
    Listens to forwarded messages from other logdispatchr instances. Please
    see the "models" page of the documentation to know more about the
    exchange format

    :param host: the host to bind to. The most common is 0.0.0.0, to listen to
                 all interfaces, but localhost or 127.0.0.1 are a possibility
    :type host: str
    :param port: the port we should listen to
    :type port: int
    """
    class UDPMessagePackServer(socketserver.UDPServer):
        def __init__(self, host, port, message_queue):
            self.message_queue = message_queue
            self.key = None
            super().__init__((host, port),
                             LogdispatchrUDPInput.UDPMessagePackHandler)

    class UDPMessagePackHandler(socketserver.DatagramRequestHandler):
        def handle(self):
            data = bytes.decode(self.request[0].strip())
#            socket = self.request[1]
            m = Message(msgpack.unpackb(data))
            # Don't update the key, since it is a forward.
            # but let's check for its presence
            if 'key' not in m:
                logger.warning('got forwarded message without a key: %s', m)
            logger.debug('got UDP Logdispatchr message: %s from %s',
                         m, self.client_address[0])
            self.server.message_queue.put(m)

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 5140)
        super().__init__(**kwargs)
        self.setup()

    def setup(self):
        self.server = LogdispatchrUDPInput.UDPMessagePackServer(
                self.host, self.port, self.messages)
        self.serverthread = threading.Thread(target=self.server.serve_forever)
        self.serverthread.setDaemon(True)
        self.serverthread.start()
        logger.info("successfully started Logdispatchr \
                message server on %s:%s", self.host, self.port)
