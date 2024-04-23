import contextlib
import dataclasses
import os
import time
import threading
import typing

import uvicorn
import uvicorn.logging

import agent.service
import agent.utils.logger
import agent.utils.consts


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
    ppe_agent = agent.service.PPEAgentService({
        'credentials': {
            'email': os.getenv('PPE_AGENT_EMAIL'),
            'password': os.getenv('PPE_AGENT_PASSWORD')
        }
    })
    server = ThreadedPPEServer({
        'app': ppe_agent._app,  # pylint: disable=protected-access
        'host': 'localhost',
        'port': os.getenv('PPE_AGENT_PORT', '8000')
    })

    try:
        ppe_agent.logger.info('Starting PPE service server')
        server.start()
    except KeyboardInterrupt:
        ppe_agent.logger.info('Shutting down PPE service server')
        ppe_agent.logout()
        server.stop()


if __name__ == '__main__':
    main()
