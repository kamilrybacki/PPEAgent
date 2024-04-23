import fastapi
import fastapi.responses

import agent.utils.consts


GENERAL_ROUTER = fastapi.APIRouter()


@GENERAL_ROUTER.get('/')
async def get_root_path(request: fastapi.Request) -> fastapi.responses.Response:
    assets_path: str = request.app.extra.get(
        agent.utils.consts.AGENT_CONFIG_FIELD
    ).assets_path
    return fastapi.responses.HTMLResponse(
        content=open(f'{assets_path}/index.html', encoding='utf-8').read(),
    )


@GENERAL_ROUTER.get('/health')
async def get_health_check() -> fastapi.responses.Response:
    return fastapi.responses.JSONResponse(
        content={'status': 'ok'},
    )
