import os
from device_manager import manager
from loguru import logger
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

SECRET_TOKEN = os.environ.get('SECRET_BOT_TOKEN')


@app.get('/door/open')
async def open_admin_request(secret_token: str):
    if secret_token != SECRET_TOKEN:
        logger.info('received incorrect token')
        return HTTPException(status_code=403, detail="Incorrect token")
    manager.door_magnet.open()
    return 'ok'


@app.get('/door/close')
async def close_admin_request(secret_token: str):
    if secret_token != SECRET_TOKEN:
        logger.info('received incorrect token')
        return HTTPException(status_code=403, detail="Incorrect token")
    manager.door_magnet.close()
    return 'ok'


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8085)
