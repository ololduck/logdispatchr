import unittest
import logdispatchr.core
from logdispatchr import formatters
from logdispatchr.models import InvalidConfigurationError


class LogdispatchrGenericTest(unittest.TestCase):
    def test_get_raw_formatter(self):
        self.assertIsInstance(formatters.get_formatter('raw_message'),
                              formatters.RawMessageFormatter)

    def test_get_formatter_without_config(self):
        with self.assertRaises(InvalidConfigurationError):
            formatters.get_formatter('whatever')


class LogdispatchrBasicFormatterTest(unittest.TestCase):
    def setUp(self):
        logdispatchr.core.CURRENT_CONFIG = logdispatchr.core.ConfigParser._get_empty_config()
        logdispatchr.core.CURRENT_CONFIG.config['formatters'] = {}
        logdispatchr.core.CURRENT_CONFIG.config['formatters']['test_formatter'] = {
            'class': 'BaseFormatter',
            'format_string': '{message}\n'
        }
        self.f = formatters.get_formatter('test_formatter')

    def test_get_named_formatter(self):
        self.assertIsInstance(self.f,
                              formatters.BaseFormatter)
        self.assertEqual(self.f.format(**{'key': 'test', 'message': 'hello'}),
                         'hello\n')

    def test_get_named_formatter_different_format_string(self):
        logdispatchr.core.CURRENT_CONFIG.config['formatters']['test_formatter']['format_string'] = '{key}: {message}\n'
        logdispatchr.core.CURRENT_CONFIG.config['formatters']['test_formatter']['class'] = 'BaseFormatter'
        self.f = formatters.get_formatter('test_formatter')
        self.assertIsInstance(self.f,
                              formatters.BaseFormatter)
        self.assertEqual(self.f.format(**{'key': 'test', 'message': 'hello'}),
                         'test: hello\n')

if __name__ == '__main__':
    unittest.main()
