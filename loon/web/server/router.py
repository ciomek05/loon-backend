from fastapi import APIRouter, Request

from loon.web import get_mqtt_manager
from loon.web.auth.middleware import authenticated

router = APIRouter(prefix="/server", tags=["server"])


@router.post("/info/request")
@authenticated
async def request_server_info(request: Request):
    get_mqtt_manager().publish("loon/server/info/request")
    return 200
