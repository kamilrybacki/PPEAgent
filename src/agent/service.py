import contextlib
import dataclasses
import logging
import requests

import fastapi

import agent.routers.general

import agent.utils.config
import agent.utils.logger
import agent.utils.retry

IMPLEMENTED_ROUTERS = [
  agent.routers.general.GENERAL_ROUTER,
]


@dataclasses.dataclass
class PPEAgentService:
  config: dict[str, str]
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
  logger: logging.Logger = dataclasses.field(init=False)

  def __post_init__(self) -> None:
    self.logger = agent.utils.logger.get_ppe_logger(
      level=self.config.pop('logging_level', 'info')
    )
    self._credentials = agent.utils.config.PPECredentials(
      **self.config.pop('credentials')
    )

    @contextlib.asynccontextmanager
    async def application_bootstrap(app: fastapi.FastAPI):
      self.login()
      for router in IMPLEMENTED_ROUTERS:
        app.include_router(router)
      yield
      self.logout()

    self._app = fastapi.FastAPI(
      lifespan=application_bootstrap
    )

  def login(self) -> None:
    self.logger.info('Logging into Energa service')
    with agent.utils.retry.retry_procedure():
      response = self._energa_session.post(
          url=agent.utils.config.PPE_LOGIN_URL,
          data=self._credentials.get_form_data(),
      )
      response.raise_for_status()
      self.logger.info('Successfully logged into Energa service')

  def logout(self, *args, **kwargs) -> None:  # pylint: disable=unused-argument
    self.logger.info('Logging out from Energa service')
    with agent.utils.retry.retry_procedure():
      self._energa_session.get(agent.utils.config.PPE_LOGOUT_URL)
      self.logger.info('Successfully logged out from Energa service')
      self._energa_session.close()
