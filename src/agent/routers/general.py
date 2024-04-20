import fastapi
import fastapi.responses

GENERAL_ROUTER = fastapi.APIRouter()


@GENERAL_ROUTER.get('/')
async def get_root_path() -> fastapi.responses.Response:
    return fastapi.responses.JSONResponse({
        'Hello': 'World'
    })
