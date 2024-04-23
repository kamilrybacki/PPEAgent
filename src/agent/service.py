import contextlib
import dataclasses
import logging
import re
import typing

import fastapi
import requests

import agent.routers.general
import agent.routers.energa

import agent.utils.config
import agent.utils.consts
import agent.utils.logger
import agent.utils.retry

IMPLEMENTED_ROUTERS = [
    agent.routers.general.GENERAL_ROUTER,
    agent.routers.energa.MEASUREMENTS_ROUTER,
]


@dataclasses.dataclass
class PPEAgentService:
    config: dict[str, typing.Any]
    logger: logging.Logger = dataclasses.field(init=False)
    _config: agent.utils.config.PPEAgentConfig = dataclasses.field(
        init=False,
        default_factory=agent.utils.config.PPEAgentConfig
    )
    _credentials: agent.utils.config.PPECredentials = dataclasses.field(
        init=False,
        repr=False
    )
    _app: fastapi.FastAPI = dataclasses.field(
        init=False,
        default_factory=fastapi.FastAPI
    )
    _energa_session: requests.Session = dataclasses.field(
        init=False,
        default_factory=requests.Session
    )

    def __post_init__(self) -> None:
        self._credentials = agent.utils.config.PPECredentials(
            **self.config.pop('credentials')
        )
        self.logger = agent.utils.logger.initialize_loggers(
            self._config.log_level,
            self._config.logging_format
        )

        @contextlib.asynccontextmanager
        async def application_bootstrap(app: fastapi.FastAPI):
            self.login()
            for router in IMPLEMENTED_ROUTERS:
                app.include_router(router)
            yield
            self.logout()

        self._app = fastapi.FastAPI(
            lifespan=application_bootstrap,
            root_path=self._config.root_path,
        )

    def login(self) -> None:
        self.logger.info('Logging into Energa service')
        with agent.utils.retry.retry_procedure(
            max_retries=self._config.max_retries
        ):
            current_page_content = self._energa_session.get(
                agent.utils.consts.PPE_LOGIN_URL
            ).text
            fetched_csrf_token_matches = re.search(
                r'name="_antixsrf" value="(.+?)"',
                current_page_content
            )
            if fetched_csrf_token_matches is None:
                raise ValueError('Could not fetch CSRF token')
            fetched_csrf_token = fetched_csrf_token_matches[1]
            response = self._energa_session.post(
                url=agent.utils.consts.PPE_LOGIN_URL,
                data={
                    '_antixsrf': fetched_csrf_token,
                } | self._credentials.get_form_data()
            )
            response.raise_for_status()
            self._credentials.id = self.get_meter_id()
            self._app.extra[
                agent.utils.consts.AGENT_METER_ID_FIELD
            ] = self._credentials.id
            self._app.extra[
                agent.utils.consts.AGENT_ENERGA_SESSION_FIELD
            ] = self._energa_session
            self._app.extra[
                agent.utils.consts.AGENT_CONFIG_FIELD
            ] = self._config
            self.logger.info('Successfully logged into Energa service')

    def get_meter_id(self) -> int:
        '''
        UIses a regex to fetch the meter ID from the basic_data_script (scraped page source), which is located under the following part of fetched HTML content:
        <script type="text/javascript">
            meters.list.push({
                id: 12345678,
                ppe: '****',
                tmp: '1',
                tariffCode: 'G11',
                name: '****',
            })
        </script>
        The regex should return the ID of the meter, which is 12345678 in this case
        '''
        with agent.utils.retry.retry_procedure(
            max_retries=self._config.max_retries
        ):
            basic_data_script_fetch_response = self._energa_session.get(
                agent.utils.consts.PPE_DATA_SCRIPT_BASE_URL
            )
            basic_data_script_fetch_response.raise_for_status()
            basic_data_script_matches = re.search(
                r'meters\.list\.push\({\s+id: (\d+),',
                basic_data_script_fetch_response.text
            )
            if basic_data_script_matches is None:
                raise ValueError('Could not fetch meter ID')
            return int(basic_data_script_matches[1])

    def logout(self, *args, **kwargs) -> None:  # pylint: disable=unused-argument
        self.logger.info('Logging out from Energa service')
        # To ensure that the logout procedure is executed when Ctrl+C is being pressed continuously, we need to ignore KeyboardInterrupt
        with agent.utils.retry.retry_procedure(
            max_retries=self._config.max_retries,
            ignored=[KeyboardInterrupt]  # type: ignore
        ):
            self._energa_session.get(agent.utils.consts.PPE_LOGOUT_URL)
            self.logger.info('Successfully logged out from Energa service')
            self._energa_session.close()
