import logging
import typing

import agent.utils.consts


def get_uvicorn_logger_config(level: str) -> dict[str, typing.Any]:
    logging_level = logging._nameToLevel[level]  # pylint: disable=protected-access
    return {
        'version': 1,
        'formatters': {
            name: {
                '()': f'uvicorn.logging.{name.title()}Formatter',
                'format': agent.utils.consts.DEFAULT_GENERAL_LOGGING_FORMAT,
                'style': '{',
                'use_colors': True,
            }
            for name in ['default', 'access']
        },
        'handlers': {
            name: {
                'class': 'logging.StreamHandler',
                'formatter': name,
            }
            for name in ['default', 'access']
        },
        'loggers': {
            'uvicorn.error': {
                'handlers': ['default'],
                'level': logging_level,
                'propagate': False
            },
            'uvicorn.access': {
                'handlers': ['access'],
                'level': logging_level,
                'propagate': False
            },
        },
    }
