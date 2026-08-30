import asyncio

from loon.web.users.models import User

user_threads = {}
user_world_requests = {}


async def send_to_player(user: User, msg):
    queue = user_threads.get(user.uuid)
    if queue is not None:
        await queue.put(msg)


def get_player_thread(user: User):
    return user_threads.get(user.uuid)


async def get_user_messages(user: User):
    queue = user_threads.get(user.uuid)
    if queue is None:
        return

    while True:
        yield await queue.get()


def subscribe_player(user: User):
    queue = asyncio.Queue()
    user_threads[user.uuid] = queue
    user_world_requests[user.uuid] = set()

    return user_threads[user.uuid]


def unsubscribe_player(user: User):
    user_threads.pop(user.uuid, None)
    user_world_requests.pop(user.uuid, None)
