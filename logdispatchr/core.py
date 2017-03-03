# -*- coding:utf-8 -*-

import toml
import queue
import logging
import logging.config
import threading
import logdispatchr.inputs
import logdispatchr.outputs
import logdispatchr.formatters
from logdispatchr.models import InvalidConfigurationError

from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigParser(object):
    """
    Reads a configuration file and exposes its contents to the application
    as python objects
    """

    @staticmethod
    def _get_empty_config():
        return ConfigParser('', empty=True)

    def __init__(self, config_path: str, empty=False):
        self.config = {}
        if not empty:
            self.read(config_path)
        self.get = self.config.get

    def read(self, filepath: str) -> None:
        with open(filepath) as f:
            self.config = toml.loads(f.read())
        logger.debug('parsed config: %s', self.config)

    def get_declared_inputs(self) -> List[logdispatchr.inputs.BaseInput]:
        inputs = []
        for _input in self.config.get('inputs', ()):
            logger.debug('Getting input %s from config file', _input)
            input_config = self.config['inputs'][_input]
            if "class" not in input_config:
                raise InvalidConfigurationError('Missing "class" attribute for \
                %s' % _input)
            inputs.append(
                    self._instanciate_class(logdispatchr.inputs,
                                            input_config))
        return inputs

    # TODO: factorize get_declared_{{in,out}puts,formatters}
    def get_declared_outputs(self) -> List[logdispatchr.outputs.BaseOutput]:
        outputs = []
        for _output in self.config.get('outputs', ()):
            logger.debug('Getting output %s from config file', _output)
            output_config = self.config['outputs'][_output]
            if "class" not in output_config:
                raise InvalidConfigurationError('Missing "class" attribute for \
                 %s' % _output)
            outputs.append(
                    self._instanciate_class(logdispatchr.outputs,
                                            output_config))
        return outputs

    def get_declared_formatters(self) -> List[logdispatchr.formatters.BaseFormatter]:
        formatters = []
        for _formatter in self.config.get('formatters', ()):
            logger.debug('Getting formatter %s from config file', _formatter)
            formatter_config = self.config['formatters'][_formatter]
            if 'class' not in formatter_config:
                raise InvalidConfigurationError('Missing "class" attribute for \
                 %s' % formatter_config)
            formatter_config['uid'] = _formatter
            formatters.append(self._instanciate_class(logdispatchr.formatters,
                                                      formatter_config))
        return formatters

    def _instanciate_class(self, module, config: Dict[str, str]) -> Any:
        logger.debug(config)
        clazz = getattr(module, config.pop('class'))
        return clazz(**config)


CURRENT_CONFIG = Optional[ConfigParser]


class LogDispatcher(object):
    """
    Core application. The Great Orchestrator (tm).
    Everything shall be rewritten with asyncio
    """
    def __init__(self, config_path: str):
        global CURRENT_CONFIG
        self.config = ConfigParser(config_path)
        CURRENT_CONFIG = self.config
        self.inputs = self.config.get_declared_inputs()
        self.outputs = self.config.get_declared_outputs()
        self.mainqueue = queue.Queue(self.config.get('mainqueue_max_size', 100))

    def mainloop(self):  # asynciiiioooooo
        logger.info("Entering main event loop")
        inputs_thread = threading.Thread(target=self.read_inputs)
        inputs_thread.setDaemon(True)
        output_thread = threading.Thread(target=self.write_outputs)
        output_thread.setDaemon(True)
        logger.debug('starting input listener thread')
        inputs_thread.start()
        logger.debug('starting output listener thread')
        output_thread.start()
        logger.info('ready')
        inputs_thread.join()
        output_thread.join()

    def read_inputs(self):
        while True:
            for _input in self.inputs:
                if _input.has_available_message:
                    logger.debug("Got message from input %s, putting in queue",
                                 str(_input))
                    self.mainqueue.put(_input.get())

    def write_outputs(self):
        while True:
            msg = self.mainqueue.get()
            logger.debug('Got a message to process: %s', msg)
            for output in self.outputs:
                output.accept(msg)
