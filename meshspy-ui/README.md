# 🛰️ MeshSpy UI

Interfaccia Web moderna per visualizzare nodi MeshTastic in tempo reale su mappa con zoom, log dal backend e configurazione Wi-Fi.

---

## ⚙️ Requisiti

- Node.js (18+ consigliato)
- npm

---

## ▶️ Avvio in modalità sviluppo

npm install
npm run dev
Visita http://localhost:5173

🔁 La UI si aggiornerà automaticamente su ogni modifica.

🌐 Comunicazione con backend
Il frontend comunica con FastAPI su http://localhost:8000.

Tipo	Percorso	Funzione
HTTP	/nodes	Dati dei nodi
HTTP	/metrics	Statistiche di sistema
WS	/ws/logs	Live log
HTTP POST	/request-location	Richiesta posizione nodo
HTTP POST	/wifi-config	Creazione file wifi.yaml

Configurabile via .env:

env

VITE_API=http://localhost:8000
🗺️ Funzioni supportate
Visualizzazione su mappa Leaflet (OpenStreetMap)

Marker con zoom e popup

Sidebar con nodi attivi e cliccabili

Log live dal backend via WebSocket

Configurazione Wi-Fi direttamente via UI

Visualizzazione metrica (estendibile)

🧱 Struttura
css

src/
├── components/
│   ├── App.jsx
│   ├── Sidebar.jsx
│   ├── MapView.jsx
│   ├── LogViewer.jsx
│   ├── Topbar.jsx
│   ├── Metrics.jsx
│   └── WifiDialog.jsx
├── lib/
│   ├── api.js
│   └── MapContext.jsx
├── index.css
└── main.jsx
📦 Build produzione
bash

npm run build
I file verranno generati in dist/.

Puoi servirli con qualsiasi server statico oppure integrarlo in un'app Electron.

🧪 Debug consigliato
Log visibili nella sezione "Live Log"

Zoom e marker cliccabili con popup

Console browser attiva per log tecnici

📄 Licenza
MIT — uso libero per progetti open e commerciali.
Progetto sviluppato per MeshSpy.