import json
import random

from loon.web.users.state import user_threads

PLAYER_EVENT_SUFFIXES = ("died", "joined", "left")

DEATH_BY_DAMAGE = {
    "fall": (
        "{username} fell from a high place",
        "{username} forgot to tie their shoes",
    ),
    "fire": (
        "{username} forgot fire burns",
        "{username} was engulfed in flames",
    ),
    "drown": (
        "{username} drowned",
    ),
    "blast": (
        "{username} blew up",
    ),
    "combat": (
        "{username} was slain",
        "{username} was pummeled to death",
    ),
    "generic": (
        "{username} died",
        "{username} withered away",
    ),
}

DEATH_BY_KILLER = {
    "fall": (
        "{username} was doomed to fall by {killer}",
    ),
    "fire": (
        "{username} walked into fire whilst fighting {killer}",
    ),
    "drown": (
        "{username} drowned whilst trying to escape {killer}",
    ),
    "blast": (
        "{username} was blown up by {killer}",
    ),
    "combat": (
        "{username} was slain by {killer}",
        "{username} was killed by {killer}",
        "{username} was slain by {killer} using magic",
        "{username} got finished off by {killer}",
    ),
    "generic": (
        "{username} was slain by {killer}",
        "{username} was killed by {killer}",
    ),
}

DEATH_BY_KILLER_DEFAULT = DEATH_BY_KILLER["combat"]


def get_random(templates, **kwargs):
    return random.choice(templates).format(**kwargs)


async def marquee_handler(client, userdata, msg):
    prefix = "loon/player/"

    if not msg.topic.startswith(prefix):
        return

    rest = msg.topic[len(prefix):]
    _, _, subtopic = rest.partition("/")

    if subtopic not in PLAYER_EVENT_SUFFIXES:
        return

    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        return

    username = data["player"]["username"]

    if subtopic == "died":
        killer = data.get("killer")
        damage_type = data.get("damageType")

        if killer:
            templates = DEATH_BY_KILLER.get(damage_type, DEATH_BY_KILLER_DEFAULT)
            message = get_random(templates, username=username, killer=killer)
        elif damage_type in DEATH_BY_DAMAGE:
            message = get_random(DEATH_BY_DAMAGE[damage_type], username=username)
        elif damage_type:
            message = f"{username} died of {damage_type}"
        else:
            message = f"{username} died"
    elif subtopic == "joined":
        message = f"{username} joined the game"
    else:
        message = f"{username} left the game"

    envelope = json.dumps({"topic": "server/marquee", "payload": {"message": message}})

    for queue in list(user_threads.values()):
        await queue.put(envelope)
