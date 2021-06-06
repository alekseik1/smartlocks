import os
import asyncio
from device_manager import manager
from loguru import logger
from fastapi import FastAPI, HTTPException, BackgroundTasks
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

SECRET_TOKEN = os.environ.get('SECRET_BOT_TOKEN')


async def close_door_after_delay(delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    manager.door_magnet.close()


@app.get('/door/open')
async def open_admin_request(secret_token: str, background_tasks: BackgroundTasks):
    if secret_token != SECRET_TOKEN:
        logger.info('received incorrect token')
        return HTTPException(status_code=403, detail="Incorrect token")
    manager.door_magnet.open()
    background_tasks.add_task(close_door_after_delay, delay_seconds=10)
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
