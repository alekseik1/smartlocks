import asyncio
import os

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from loguru import logger

from device_manager import DeviceManager

app = FastAPI()
manager = DeviceManager()
load_dotenv()

SECRET_TOKEN = os.environ["SECRET_BOT_TOKEN"]
logger.debug(f"secret token is: {SECRET_TOKEN}")


async def close_door_after_delay(delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    manager.door_magnet.close()


async def change_text(delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    manager.lcd_display.print_lcd("PLACE CARD \n ON READER")


@app.get("/door/open")
async def open_admin_request(secret_token: str, background_tasks: BackgroundTasks):
    if secret_token != SECRET_TOKEN:
        logger.info("received incorrect token")
        return HTTPException(status_code=403, detail="Incorrect token")
    logger.debug(f"token: {secret_token}")
    logger.info(f"received door open signal with correct token, opening")
    manager.door_magnet.open()
    manager.lcd_display.print_lcd("HACKING DETECTED\nopening door")
    background_tasks.add_task(close_door_after_delay, delay_seconds=10)
    background_tasks.add_task(change_text, delay_seconds=3)
    return "ok"


@app.get("/door/close")
async def close_admin_request(secret_token: str):
    if secret_token != SECRET_TOKEN:
        logger.info("received incorrect token")
        return HTTPException(status_code=403, detail="Incorrect token")
    manager.door_magnet.close()
    return "ok"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8085)
