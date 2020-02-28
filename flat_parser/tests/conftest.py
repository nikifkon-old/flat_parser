import logging

import pytest

from flat_parser.utils.log import setup_logging


TEST_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'class': 'logging.Formatter',
            'format': '[%(levelname)s]: %(message)s'
        },
        'verbose': {
            'class': 'logging.Formatter',
            'format': '[%(levelname)s:%(name)s]: %(message)s'
        },
        'test': {
            'class': 'logging.Formatter',
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'flat_parser.utils.log.FileHandlerUTFEncoding',
            'filename': 'flat_parser/tests/flat_parser.log',
            'formatter': 'test',
            'mode': 'w'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    },
}


@pytest.fixture
def logger():
    setup_logging(config=TEST_LOGGING_CONFIG)
    return logging.getLogger()
