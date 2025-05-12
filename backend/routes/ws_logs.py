from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import os

router = APIRouter()

# 📄 Percorso del file di log da leggere (modifica se necessario)
log_path = "meshspy.log"  # puoi anche usare "logs/meshspy.log" o path assoluto

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()

    try:
        # Verifica se il file esiste
        if not os.path.exists(log_path):
            await websocket.send_text(f"[server] File log non trovato: {log_path}")
            return

        with open(log_path, "r") as f:
            f.seek(0, os.SEEK_END)  # tail -f: vai in fondo

            while True:
                line = f.readline()
                if line:
                    await websocket.send_text(line.strip())
                await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("[ws] connessione chiusa")

    except Exception as e:
        await websocket.send_text(f"[server] errore lettura log: {str(e)}")
