# -*- coding:utf-8 -*-


class Message(dict):
    """
    The base message class
    """
    pass


class InvalidMessageError(TypeError):
    pass


class InvalidConfigurationError(RuntimeError):
    pass
