# Meshtastic Remote Node Manager

Gestione remota di nodi Meshtastic con architettura server-client via WebSocket. Progetto scritto in Python, con interfaccia GUI PyQt5 lato server e client su Raspberry Pi Zero.

## 📦 Struttura del progetto

```
meshtastic-remote/
├── server/                 # GUI + WebSocket Server
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── client/                 # Client Raspberry Pi + meshtastic-cli
│   ├── client_pi_meshtastic.py
│   ├── config.json
│   ├── requirements.txt
│   ├── client_pi.service
│   └── README.md
├── setup.sh                # Script installazione automatica per client
└── README.md               # Questo file
```

---

## 🚀 Funzionalità principali

### ✅ Server (Ubuntu desktop/laptop)

* GUI PyQt5 con elenco client remoti attivi
* Comandi diretti ai nodi: `status`, `send <msg>`
* WebSocket server per comunicazione bidirezionale

### ✅ Client (Raspberry Pi Zero)

* Connessione automatica al server via WebSocket
* Invio periodico dello stato nodo ogni 30 secondi
* Ricezione ed esecuzione comandi dal server
* Supporta avvio automatico tramite systemd

---

## 🖥️ Server - Avvio rapido

```bash
cd server
pip install -r requirements.txt
python main.py
```

> Il server avvia un WebSocket listener su porta `8765` e una GUI con lista nodi attivi.

---

## 🍓 Client - Installazione 1 comando

```bash
curl -sSL https://your-server.com/setup.sh | bash
```

### Contenuto `config.json` (creato automaticamente):

```json
{
  "id": "raspberry-001",
  "server_url": "ws://<SERVER_IP>:8765"
}
```

### Systemd (avvio al boot)

```bash
sudo cp client/client_pi.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl enable client_pi.service
sudo systemctl start client_pi.service
```

---

## 🔧 Requisiti

### Server:

* Python 3.7+
* PyQt5
* websockets

### Client:

* Raspberry Pi Zero (collegato via USB al nodo Meshtastic)
* Python 3.7+
* `meshtastic-cli` installato (`pip install meshtastic`)

---

## 🛠️ Manutenzione futura

* [ ] Logging su file degli eventi server
* [ ] UI per monitoraggio in tempo reale (batteria, GPS, messaggi)
* [ ] Dashboard web alternativa

---

## 📖 Licenza

MIT License

---

## 🧠 Autore

**Code Copilot** – GPT personalizzato per assistenza programmazione.

---

Contributi, feedback o fork sono benvenuti! 🎉
