import fastapi
import fastapi.responses

import agent.utils.consts

GENERAL_ROUTER = fastapi.APIRouter()


@GENERAL_ROUTER.get('/')
async def get_root_path() -> fastapi.responses.Response:
    return fastapi.responses.HTMLResponse(
        content=open(f'{agent.utils.consts.DEFAULT_GENERAL_ASSETS_PATH}/index.html', encoding='utf-8').read(),
    )


@GENERAL_ROUTER.get('/health')
async def get_health_check() -> fastapi.responses.Response:
    return fastapi.responses.JSONResponse(
        content={'status': 'ok'},
    )
