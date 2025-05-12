from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import os

router = APIRouter()

# Percorso sicuro e relativo al backend
log_path = os.path.join(os.path.dirname(__file__), "../logs/meshspy.log")
log_path = os.path.abspath(log_path)

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()

    try:
        if not os.path.exists(log_path):
            await websocket.send_text(f"[server] File log non trovato: {log_path}")
            return

        with open(log_path, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    await websocket.send_text(line.strip())
                await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("[ws] Connessione chiusa")

    except Exception as e:
        await websocket.send_text(f"[server] errore lettura log: {str(e)}")
