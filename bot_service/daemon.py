import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger

from door_service.daemon import CONTROL_PORT
from log_utils import setup_logger

app = FastAPI()


@app.get("/door/open")
async def open_admin_request(secret_token: str):
    if secret_token != SECRET_TOKEN:
        logger.info("received incorrect token")
        return HTTPException(status_code=403, detail="Incorrect token")
    for action in ("unlock", "lock"):
        logger.info(f"sending {action} signal")
        r = requests.get(f"http://localhost:{CONTROL_PORT}/{action}")
        if r.status_code == 200:
            logger.debug("request completed successfully")
        elif r.status_code == 400:
            logger.warning(f"button request was not success, text={r.text}")
    return "ok"


@app.get("/health_check")
async def say_alive():
    return "ok"


if __name__ == "__main__":
    setup_logger()
    load_dotenv()
    SECRET_TOKEN = os.environ["SECRET_BOT_TOKEN"]
    logger.debug(f"secret token is: {SECRET_TOKEN}")
    uvicorn.run(app, host="0.0.0.0", port=8085)
