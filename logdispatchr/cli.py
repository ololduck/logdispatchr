# -*- coding: utf-8 -*-

import click
import logging

from logdispatchr.core import LogDispatcher


console_formatter = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setFormatter(console_formatter)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(console)


@click.command()
@click.option('--config', default='/etc/config.toml',
              help='use this file for the configuration')
def main(config):
    """Console script for logdispatchr"""
    root.debug("trying to read config file...")
    app = LogDispatcher(config)
    root.info('launching main loop...')
    app.mainloop()

if __name__ == "__main__":
    main()
