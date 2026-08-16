import asyncio
import json
import threading

import paho.mqtt.client as mqtt

from config import settings
from loon import logger
from loon.mqtt.handlers.change_password_request import change_password_handler
from loon.mqtt.handlers.marquee import marquee_handler
from loon.mqtt.handlers.player import player_handler
from loon.mqtt.handlers.register_request import register_request_handler
from loon.mqtt.handlers.server import server_handler
from loon.mqtt.handlers.world import world_handler


class MQTTManager:
    BASE_HANDLERS = [player_handler, register_request_handler, world_handler, server_handler, marquee_handler, change_password_handler]

    def __init__(self, inject_handlers = None):
        if inject_handlers is None:
            inject_handlers = []

        self.client = mqtt.Client()
        self.thread = None
        self.loop = asyncio.get_running_loop()

        self.handlers = self.BASE_HANDLERS + inject_handlers

    @staticmethod
    def setup_and_start():
        mqtt_client = MQTTManager()
        mqtt_client.connect()
        mqtt_client.start()
        return mqtt_client

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_topic
        self.client.username_pw_set(username=settings.mqtt.username, password=settings.mqtt.password)
        self.client.reconnect_delay_set(min_delay=1, max_delay=60)
        self.client.connect_async(settings.mqtt.host, settings.mqtt.port)

    def start(self):
        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self.thread.start()
        return self.thread

    @staticmethod
    def on_connect(client, userdata, flags, reason_code):
        logger.info(f"MQTT connected (rc={reason_code})")
        client.subscribe("loon/#")

    @staticmethod
    def on_disconnect(client, userdata, reason_code):
        logger.warning(f"MQTT disconnected (rc={reason_code}). Reconnecting...")

    def on_topic(self, client, userdata, msg):
        async def handle_message():
            try:
                data = json.loads(msg.payload.decode())
            except json.decoder.JSONDecodeError:
                return

            if settings.mqtt.log_data:
                logger.info(f"[Received] {data}.")

            for handler in self.handlers:
                try:
                    await handler(client, userdata, msg, data)
                except Exception as e:
                    logger.error(f'Got exception: {e}')

        asyncio.run_coroutine_threadsafe(handle_message(), self.loop)

    def publish(self, topic: str, payload: mqtt.PayloadType = None, qos: int = 0, retain: bool = False) -> mqtt.MQTTMessageInfo:
        return self.client.publish(topic, payload, qos, retain)
