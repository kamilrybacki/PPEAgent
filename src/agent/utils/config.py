import dataclasses
import os
import re
import typing

import configparser

import agent.utils.consts


@dataclasses.dataclass
class PPECredentials:
    email: str
    password: str = dataclasses.field(repr=False)
    id: int | None = dataclasses.field(default=None)

    __EMAIL_REGEX = r"^\S+@\S+\.\S+$"

    def __post_init__(self) -> None:
        self._validate_email()
        self.password = self.password.strip()

    def _validate_email(self) -> None:
        self.email = self.email.strip()
        if not re.match(self.__EMAIL_REGEX, self.email):
            raise ValueError('Invalid email address')

    def get_form_data(self) -> dict[str, typing.Any]:
        return {
            agent.utils.consts.PPE_LOGIN_FORM_USERNAME_ID: str(self.email),
            agent.utils.consts.PPE_LOGIN_FORM_PASSWORD_ID: str(self.password)
        } | agent.utils.consts.PPE_LOGIN_FORM_ADDITIONAL_DATA


@dataclasses.dataclass
class PPEAgentConfig:
    logging_format: str = dataclasses.field(default=agent.utils.consts.DEFAULT_GENERAL_LOGGING_FORMAT)
    assets_path: str = dataclasses.field(default=agent.utils.consts.DEFAULT_GENERAL_ASSETS_PATH)
    max_retries: int = dataclasses.field(default=agent.utils.consts.DEFAULT_GENERAL_MAX_RETRIES)
    timeout: int = dataclasses.field(default=agent.utils.consts.DEFAULT_AGENT_TIMEOUT)
    root_path: str = dataclasses.field(default=agent.utils.consts.DEFAULT_AGENT_ROOT_PATH)
    log_level: str = dataclasses.field(default='info')

    def __post_init__(self) -> None:
        if config_path := os.environ.get('PPE_AGENT_CONFIG'):
            self.load_config(config_path)
        self.logging_format = self.logging_format.strip()
        self.assets_path = self.assets_path.strip()
        if not self.root_path.startswith('/'):
            raise ValueError('Root path must start with a forward slash')
        self.root_path = self.root_path.strip().removesuffix('/')
        if self.max_retries < 0:
            raise ValueError('Max retries must be a non-negative integer')
        if self.timeout < 0:
            raise ValueError('Timeout must be a non-negative integer')

    def load_config(self, config_path: str) -> None:
        if not os.path.exists(config_path):
            raise FileNotFoundError('Config file not found, chech the value of PPE_CONFIG_PATH environment variable')
        config = configparser.RawConfigParser()
        config.read(config_path)
        if 'AGENT' not in config:
            raise ValueError('Config file must contain an [AGENT] section')
        self.logging_format = config['AGENT'].get('logging_format', self.logging_format)
        print(self.logging_format)
        self.assets_path = config['AGENT'].get('assets_path', self.assets_path)
        self.max_retries = config['AGENT'].getint('max_retries', self.max_retries)
        self.timeout = config['AGENT'].getint('timeout', self.timeout)
        self.root_path = config['AGENT'].get('root_path', self.root_path)
        self.log_level = os.getenv('PPE_AGENT_LOG_LEVEL', self.log_level).upper()
