import enum
import logging
import typing

import agent.utils.config


@enum.unique
class LoggingLevel(enum.Enum):
  DEBUG = 'debug'
  INFO = 'info'
  WARNING = 'warning'
  ERROR = 'error'
  CRITICAL = 'critical'


def get_ppe_logger(level: LoggingLevel = LoggingLevel.INFO) -> logging.Logger:
  logging.basicConfig(
      format=agent.utils.config.GENERAL_LOGGING_FORMAT,
      level=level.value.upper(),
      style='{',
  )
  ppe_logger = logging.getLogger(agent.utils.config.AGENT_LOGGER_NAME)
  ppe_logger.setLevel(level.value.upper())
  return ppe_logger


def get_uvicorn_logger_config(level: LoggingLevel = LoggingLevel.INFO) -> dict[str, typing.Any]:
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
            'level': level.value.upper(),
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': level.value.upper(),
            'propagate': False
        },
    },
  }
