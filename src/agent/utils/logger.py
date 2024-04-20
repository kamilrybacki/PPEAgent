import logging
import typing

import agent.utils.config


def get_ppe_logger(level: str) -> logging.Logger:
    ppe_logger = logging.getLogger(agent.utils.config.AGENT_LOGGER_NAME)
    ppe_logger.setLevel(
        level=logging._nameToLevel[level]  # pylint: disable=protected-access
    )
    return ppe_logger


def get_uvicorn_logger_config(level: str) -> dict[str, typing.Any]:
    logging_level = logging._nameToLevel[level]  # pylint: disable=protected-access
    return {
        'version': 1,
        'formatters': {
            name: {
                '()': f'uvicorn.logging.{name.title()}Formatter',
                'format': agent.utils.config.GENERAL_LOGGING_FORMAT,
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
