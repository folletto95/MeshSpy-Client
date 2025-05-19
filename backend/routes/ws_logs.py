import os
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
LOG_FILE = os.path.join(LOG_DIR, "meshspy.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("meshspy")

router = APIRouter()

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    logger.info("📡 Connessione WebSocket /ws/logs aperta")
    await websocket.send_text("✅ Connessione WebSocket stabilita")  # Saluto iniziale

    try:
        with open(LOG_FILE, "r") as log_file:
            log_file.seek(0, os.SEEK_END)  # Vai in fondo

            while True:
                line = log_file.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue

                await websocket.send_text(line.strip())
    except WebSocketDisconnect:
        logger.info("❌ WebSocket /ws/logs chiusa dal client")
    except Exception as e:
        logger.exception("Errore WebSocket logs: %s", e)
        await websocket.send_text(f"Errore: {str(e)}")
