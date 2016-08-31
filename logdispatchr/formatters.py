# -*- coding:utf-8 -*-


def get_formatter(formater):
    return None


class BasicFormater(object):
    def __init__(self, format_string):
        self.format_string = format_string

    def format(self, **data):
        return self.format_string.format(**data)
