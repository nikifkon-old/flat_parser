LOGGING_CONFIG = {
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
            'class': 'logging.FileHandler',
            'filename': 'flat_parser.log',
            'formatter': 'verbose'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    },
}
