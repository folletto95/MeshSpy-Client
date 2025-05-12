from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import os

router = APIRouter()
active_connections: List[WebSocket] = []

log_path = "/var/log/meshspy/meshspy.log"  # Cambia se il file è altrove

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    async def tail_file():
        try:
            with open(log_path, "r") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        await websocket.send_text(line.strip())
                    await asyncio.sleep(0.5)
        except Exception as e:
            await websocket.send_text(f"[server] errore lettura log: {str(e)}")

    task = asyncio.create_task(tail_file())

    try:
        while True:
            await websocket.receive_text()  # per mantenere viva la connessione
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        task.cancel()
