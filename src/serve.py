import contextlib
import dataclasses
import logging
import os
import time
import threading
import typing

import uvicorn
import uvicorn.logging

import agent.service
import agent.utils.logger


@dataclasses.dataclass
class ThreadedPPEServer:
    config: dict[str, typing.Any]
    server: uvicorn.Server = dataclasses.field(init=False)
    thread: threading.Thread = dataclasses.field(init=False)
    should_exit: bool = dataclasses.field(default=False)

    def __post_init__(self):
        self.server = uvicorn.Server(
            config=uvicorn.Config(**self.config)
        )
        self.thread = threading.Thread(
            target=self.server.run
        )

    @contextlib.contextmanager
    def run_in_thread(self):
        if self.should_exit:
            self.should_exit = False
        self.thread.start()
        try:
            while not self.server.started:
                time.sleep(0.1)
            yield
        finally:
            self.should_exit = True
            self.thread.join()

    def start(self):
        with self.run_in_thread():
            while not self.should_exit:
                time.sleep(0.1)

    def stop(self):
        self.should_exit = True


def main():
    logging_level = os.getenv('PPE_AGENT_LOG_LEVEL', 'info').upper()
    logging.basicConfig(
        format=agent.utils.config.GENERAL_LOGGING_FORMAT,
        level=logging_level,
        style='{',
    )
    ppe_agent = agent.service.PPEAgentService({
        'credentials': {
            'email': os.getenv('PPE_AGENT_EMAIL'),
            'password': os.getenv('PPE_AGENT_PASSWORD')
        },
        'logging_level': logging_level
    })
    server = ThreadedPPEServer({
        'app': ppe_agent._app,  # pylint: disable=protected-access
        'host': 'localhost',
        'port': 8000,
        'log_config': agent.utils.logger.get_uvicorn_logger_config(
            level=logging_level
        )
    })

    server_logger = logging.getLogger('uvicorn')
    try:
        server_logger.info('Starting PPE service server')
        server.start()
    except KeyboardInterrupt:
        server_logger.info('Shutting down PPE service server')
        server.stop()


if __name__ == '__main__':
    main()
