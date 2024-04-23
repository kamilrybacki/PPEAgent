import os

# Configuration defaults

DEFAULT_GENERAL_LOGGING_LEVEL = 'INFO'
DEFAULT_GENERAL_LOGGING_FORMAT = '{asctime} [{processName}] {levelname}: {message}'
DEFAULT_GENERAL_ASSETS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
DEFAULT_GENERAL_MAX_RETRIES = 3
DEFAULT_AGENT_TIMEOUT = 10
DEFAULT_AGENT_ROOT_PATH = '/'

# Implementation details - non-configurable

AGENT_CONFIG_FIELD = 'config'
AGENT_METER_ID_FIELD = 'meterId'
AGENT_ENERGA_SESSION_FIELD = 'session'
AGENT_ASSETS_PATH_FIELD = 'assetsPath'

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
PPE_DATA_SCRIPT_BASE_URL = 'https://mojlicznik.energa-operator.pl/dp/UserData.do'
PPE_DATA_CHARTS_BASE_URL = 'https://mojlicznik.energa-operator.pl/dp/resources/chart'
