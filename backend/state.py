from functools import lru_cache
from backend.services.mqtt import MQTTService

class AppState:
    def __init__(self):
        self._mqtt_service = None

    @property
    def mqtt_service(self):
        if self._mqtt_service is None:
            self._mqtt_service = MQTTService()
        return self._mqtt_service

@lru_cache()
def get_mqtt_service() -> MQTTService:
    return AppState().mqtt_service
