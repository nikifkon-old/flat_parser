import logging
import logging.config

from selenium.webdriver.remote.remote_connection import LOGGER

from flat_parser.utils.log import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER.setLevel(logging.WARNING) # don't work
