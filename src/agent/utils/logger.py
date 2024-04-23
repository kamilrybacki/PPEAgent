import logging
import logging.config
import typing

import agent.utils.consts


def initialize_loggers(
    level: str = agent.utils.consts.DEFAULT_GENERAL_LOGGING_LEVEL,
    formatting: str = agent.utils.consts.DEFAULT_GENERAL_LOGGING_FORMAT
) -> dict[str, typing.Any]:
    logging_level = logging._nameToLevel[level.upper()]  # pylint: disable=protected-access
    current_config: dict[str, typing.Any] = {
        'version': 1,
        'formatters': {
            name: {
                '()': f'uvicorn.logging.{name.title()}Formatter',
                'format': formatting,
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
            'uvicorn': {
                'handlers': ['default'],
                'level': logging_level,
                'propagate': False
            },
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
    logging.config.dictConfig(current_config)
    return current_config
