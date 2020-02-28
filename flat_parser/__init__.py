import logging

from selenium.webdriver.remote.remote_connection import LOGGER

from flat_parser.utils.log import setup_logging

setup_logging()
LOGGER.setLevel(logging.WARNING) # don't work
