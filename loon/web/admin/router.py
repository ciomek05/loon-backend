from fastapi import APIRouter
from starlette.requests import Request

from loon.web.auth.middleware import admin

router = APIRouter(prefix="/admin", tags=["admin"])

