import logging
import meshtastic.serial_interface
import time

def connect_interface(dev_path=None, retries=5):
    for attempt in range(1, retries + 1):
        try:
            logging.info(f"[Tentativo {attempt}/{retries}] Connessione al nodo su {dev_path}...")
            iface = meshtastic.serial_interface.SerialInterface(devPath=dev_path)
            return iface
        except Exception as e:
            logging.warning(f"Tentativo fallito: {e}")
            time.sleep(2)
    raise RuntimeError("Impossibile connettersi al nodo dopo più tentativi.")
