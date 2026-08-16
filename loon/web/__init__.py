from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from config import settings
from loon.mqtt.manager import MQTTManager
from loon.web.auth.middleware import JWTAuthBackend, on_auth_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mqtt_manager = MQTTManager.setup_and_start()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    AuthenticationMiddleware,
    backend=JWTAuthBackend(),
    on_error=on_auth_error,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.web.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_mqtt_manager() -> MQTTManager:
    return app.state.mqtt_manager

from loon.web.auth.router import router as auth_router
from loon.web.users.router import router as users_router
from loon.web.world.router import router as world_router
from loon.web.server.router import router as server_router
from loon.web.admin.router import router as admin_router
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(world_router)
app.include_router(server_router)
app.include_router(admin_router)
