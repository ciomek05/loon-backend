from enum import Enum


class LogTypeEnum(Enum):
    PLAYER_DEAD = "player_dead"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    PLAYER_KICKED = "player_kicked"
    PLAYER_BANNED = "player_banned"
    PLAYER_REGISTERED = "player_registered"
    PLAYER_PASSWORD_CHANGED = "player_password_changed"
