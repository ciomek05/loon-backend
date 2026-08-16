import asyncio
import threading

from fastapi import APIRouter, Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from loon.web import get_mqtt_manager
from loon.web.auth.middleware import authenticated
from loon.web.users.state import user_threads

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
@authenticated
async def me(request: Request):
    return request.user.user.model_dump(exclude={"password", "id"})

@router.post("/inventory/request")
@authenticated
async def request_inventory(request: Request):
    user = request.user.user
    get_mqtt_manager().publish(f"loon/player/{user.uuid}/inventory/full/request")

    return 200

@router.post("/online/request")
@authenticated
async def request_online(request: Request):
    user = request.user.user
    get_mqtt_manager().publish(f"loon/player/{user.uuid}/online/request")

    return 200

@router.post("/position/request")
@authenticated
async def request_position(request: Request):
    user = request.user.user
    get_mqtt_manager().publish(f"loon/player/{user.uuid}/position/request")

    return 200


@router.websocket("/me")
@authenticated
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = websocket.user.user

    queue = asyncio.Queue()
    user_threads[user.uuid] = queue

    try:
        while True:
            message = await queue.get()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        pass
    finally:
        user_threads.pop(user.uuid, None)
