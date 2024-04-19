import uvicorn
import os

import agent.service
import agent.utils.logger


def main():
    ppe_agent = agent.service.PPEAgentService({
        'email': os.getenv('PPE_AGENT_EMAIL'),
        'password': os.getenv('PPE_AGENT_PASSWORD')
    })
    uvicorn.run(
        app=ppe_agent._app,  # pylint: disable=protected-access
        host='localhost',
        port=8000,
        log_config=agent.utils.logger.get_uvicorn_logger_config(),
    )


if __name__ == '__main__':
    main()
