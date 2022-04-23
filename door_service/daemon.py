import time
from multiprocessing import Process, Queue
from queue import Full

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from loguru import logger
from starlette.requests import Request

OPEN_TIME = 5  # На сколько открывать, в секундах
CONTROL_PORT = 5050  # порт, на котором будут слушаться команды открытия


def create_app(queue) -> FastAPI:
    app = FastAPI()
    app.queue = queue
    app.include_router(router, prefix="")
    return app


def run_app(queue, port: int = 5050):
    uvicorn.run(create_app(queue), port=port)


router = APIRouter()


@router.get("/unlock")
async def unlock_order(request: Request):
    queue = request.app.queue  # type: Queue
    try:
        queue.put(1, block=True, timeout=2 * OPEN_TIME)
    except Full:
        raise HTTPException(400, "lockbox is busy, try later")
    except ValueError:
        raise HTTPException(400, "queue is closed")
    return "ok"


@router.get("/lock")
async def lock_order(request: Request):
    queue = request.app.queue  # type: Queue
    try:
        queue.put(0, block=True, timeout=2 * OPEN_TIME)
    except Full:
        raise HTTPException(400, "lockbox is busy, try later")
    except ValueError:
        raise HTTPException(400, "queue is closed")
    return "ok"


@router.get("/health_check")
async def health_check(request: Request):
    queue = request.app.queue  # type: Queue
    try:
        queue.put(None, block=True, timeout=2 * OPEN_TIME)
    except Full:
        raise HTTPException(400, "lockbox is busy, try later")
    except ValueError:
        raise HTTPException(400, "queue is closed")
    return "ok"


def handle_queue(queue: Queue):
    from multiprocessing import Lock

    from device_manager import DoorMagnet

    door_magnet = DoorMagnet(Lock())
    while True:
        try:
            command = queue.get(block=True)
            logger.debug(command)
        except ValueError:
            logger.error("queue is closed")
            raise
        if command == 1:
            door_magnet.open()
            time.sleep(OPEN_TIME)
        elif command == 0:
            ...
            door_magnet.close()
        elif command is None:
            logger.info("health check command")
        time.sleep(0.1)


if __name__ == "__main__":
    queue = Queue()
    p_server = Process(target=run_app, args=(queue, CONTROL_PORT))
    p_worker = Process(target=handle_queue, args=(queue,))
    p_server.start()
    p_worker.start()
    p_worker.join()
