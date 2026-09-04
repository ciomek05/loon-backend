from fastapi import APIRouter, Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from loon.web import get_mqtt_manager
from loon.web.auth.middleware import authenticated
from loon.web.users.models import User
from loon.web.users.schema import UserPublic
from loon.web.users.state import subscribe_player, get_user_messages, unsubscribe_player

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
@authenticated
async def me(request: Request) -> User:
    return request.user.user

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

    subscribe_player(user)

    try:
        async for message in get_user_messages(user):
            await websocket.send_text(message)
    except WebSocketDisconnect:
        pass
    finally:
        unsubscribe_player(user)