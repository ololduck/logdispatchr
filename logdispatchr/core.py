# -*- coding:utf-8 -*-

import toml
import queue
import logging
import logging.config
import threading
import logdispatchr.inputs
import logdispatchr.outputs

logger = logging.getLogger(__name__)


class ConfigParser(object):
    def __init__(self, config_path):
        self.config = {}
        self.read(config_path)
        self.get = self.config.get

    def read(self, filepath):
        with open(filepath) as f:
            self.config = toml.loads(f.read())
        logger.debug('parsed config: %s', self.config)

    def get_declared_inputs(self):
        inputs = []
        for _input in self.config.get('inputs', ()):
            logger.debug('Getting input %s from config file', _input)
            inputs.append(
                    self._instanciate_class(logdispatchr.inputs,
                                            self.config['inputs'][_input]))
        return inputs

# factorize get_declared_{in,out}puts
    def get_declared_outputs(self):
        outputs = []
        for _output in self.config.get('outputs', ()):
            logger.debug('Getting output %s from config file', _output)
            output_config = self.config['outputs'][_output]
            if "class" not in output_config:
                logger.error('invalid configuration for %s. Missing "class" attribute' % _output)
                # TODO: find a better way to handle this
                import sys
                sys.exit(1)

            outputs.append(
                    self._instanciate_class(logdispatchr.outputs,
                                            self.config['outputs'][_output]))
        return outputs

    def _instanciate_class(self, module, config):
        logger.debug(config)
        clazz = getattr(module, config.pop('class'))
        return clazz(**config)


class LogDispatcher(object):
    """
    Core application. The Great Orchestrator (tm).
    Everything shall be rewritten with asyncio
    """
    def __init__(self, config_path):
        self.config = ConfigParser(config_path)
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
                if _input.has_available_message():
                    self.mainqueue.put(_input.get())

    def write_outputs(self):
        while True:
            msg = self.mainqueue.get()
            logger.debug('Got a message to process: %s', msg)
            for output in self.outputs:
                output.accept(msg)
