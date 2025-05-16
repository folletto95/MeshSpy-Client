from pydantic import BaseModel

class Node(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    ele: float | None = None         # altitudine
    accuracy: float | None = None    # accuratezza GPS
    online: bool = True
    firmware: str | None = None      # versione firmware da nodeinfo
    variant: str | None = None       # variante hardware da nodeinfo

# Aggiunta della classe AppState per gestione centralizzata
class AppState:
    def __init__(self):
        self.nodes: dict[str, Node] = nodes
        self._mqtt_service = None

    @property
    def mqtt_service(self):
        if self._mqtt_service is None:
            from backend.services.mqtt import MQTTService  # Import lazy QUI
            self._mqtt_service = MQTTService()
        return self._mqtt_service