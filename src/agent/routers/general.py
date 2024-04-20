import fastapi
import fastapi.responses

GENERAL_ROUTER = fastapi.APIRouter()


@GENERAL_ROUTER.get('/')
async def get_root_path() -> fastapi.responses.Response:
    return fastapi.responses.HTMLResponse(
        content='''
            <html>
                <head>
                    <title>PPE Agent</title>
                </head>
                <body>
                    <h1>Welcome to PPE Agent</h1>
                </body>
            </html>
        '''
    )
