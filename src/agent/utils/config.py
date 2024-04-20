import dataclasses
import re
import typing

GENERAL_LOGGING_FORMAT = '{asctime} [{processName}] {levelname}: {message}'
GENERAL_MAX_RETRIES = 3

AGENT_ROOT_PATH = '/'
AGENT_LOGGER_NAME = 'PPEAgent'

PPE_LOGIN_URL = 'https://mojlicznik.energa-operator.pl/dp/UserLogin.do'
PPE_LOGOUT_URL = 'https://mojlicznik.energa-operator.pl/dp/UserLogout.do'

PPE_LOGIN_FORM_USERNAME_ID = 'j_username'
PPE_LOGIN_FORM_PASSWORD_ID = 'j_password'
PPE_LOGIN_FORM_ADDITIONAL_DATA = {
    'save': 'save',
    'selectedForm': 1,
    'loginNow': 'zaloguj się',
    'clientOS': 'web'
}
PPE_DATA_CHARTS_BASE_URL = 'https://mojlicznik.energa-operator.pl/dp/resources/chart'


@dataclasses.dataclass
class PPECredentials:
    email: str
    password: str = dataclasses.field(repr=False)

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
            PPE_LOGIN_FORM_USERNAME_ID: str(self.email),
            PPE_LOGIN_FORM_PASSWORD_ID: str(self.password)
        } | PPE_LOGIN_FORM_ADDITIONAL_DATA
