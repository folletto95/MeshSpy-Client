import { useMap } from "../lib/MapContext";
import { Radio, MapPin, HelpCircle, Bot } from "lucide-react";
import { addLogLine } from "./LogViewer";
import { requestNodePosition, sendCustomCommand } from "../lib/api";
import NodeActions from "./NodeActions";
import RaspberryDialog from "./RaspberryDialog";
import { useState } from "react";

export default function Sidebar() {
  const { nodes, mapRef, markersRef, selectedNodeId, setSelectedNodeId } = useMap();
  const [customCommand, setCustomCommand] = useState("");
  const [raspDialogOpen, setRaspDialogOpen] = useState(false);
  const [raspNode, setRaspNode] = useState(null);

  const handleClick = async (node) => {
    setSelectedNodeId(node.id);

    if (node.hasPosition) {
      const marker = markersRef.current[node.id];
      if (marker && mapRef.current) {
        const latlng = marker.getLatLng();
        mapRef.current.setView(latlng, 14, { animate: true });
        marker.openPopup();
        addLogLine(`📍 Zoom su ${node.name}`);
      } else {
        addLogLine(`❌ Marker non trovato per ${node.name}`);
      }
    } else {
      addLogLine(`📡 Richiesta posizione per nodo ${node.id} (${node.name})`);
      try {
        await requestNodePosition(node.id);
      } catch (err) {
        addLogLine(`❌ Errore richiesta posizione: ${err.message}`);
      }
    }
  };

  const handleSendCommand = async () => {
    if (!selectedNodeId || !customCommand) return;
    try {
      await sendCustomCommand(selectedNodeId, customCommand);
      addLogLine(`📤 Comando "${customCommand}" inviato a ${selectedNodeId}`);
      setCustomCommand("");
    } catch (err) {
      addLogLine(`❌ Errore comando: ${err.message}`);
    }
  };

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  const handleOpenRaspberry = (node) => {
    setRaspNode(node);
    setRaspDialogOpen(true);
  };

  return (
    <aside className="w-64 h-full bg-gradient-to-b from-meshtastic to-gray-900 dark:from-gray-800 dark:to-gray-900 text-white shadow-md flex flex-col">
      <div className="flex items-center gap-2 px-4 py-5 text-xl font-semibold drop-shadow">
        <Radio className="w-6 h-6" />
        MeshSpy
      </div>

      <nav className="flex-1 overflow-auto space-y-1">
        {nodes.length === 0 ? (
          <div className="px-4 py-2 text-gray-400">Nessun nodo disponibile</div>
        ) : (
          nodes.map((n) => (
            <div
              key={n.id}
              className={`flex flex-col px-4 py-2 hover:bg-gray-700 rounded cursor-pointer ${
                selectedNodeId === n.id ? "bg-gray-700 font-semibold" : ""
              }`}
              onClick={() => handleClick(n)}
            >
              <div className="flex items-center gap-2">
                {n.hasPosition ? (
                  <MapPin className="w-4 h-4 text-lime-400" />
                ) : (
                  <HelpCircle className="w-4 h-4 text-gray-400" />
                )}
                <span className="flex-1 truncate">{n.name}</span>
                {n.isRaspberry && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenRaspberry(n);
                    }}
                    title="Gestione Raspberry"
                    className="text-pink-400 hover:text-pink-300"
                  >
                    <Bot className="w-4 h-4" />
                  </button>
                )}
              </div>
              <NodeActions node={n} />
            </div>
          ))
        )}
      </nav>

      <div className="p-4 border-t border-gray-700 space-y-2">
        <label className="block text-sm text-gray-300">Comando personalizzato</label>
        <input
          type="text"
          value={customCommand}
          onChange={(e) => setCustomCommand(e.target.value)}
          placeholder='Esempio: {"cmd":"ping"}'
          className="w-full px-2 py-1 rounded bg-gray-800 text-white border border-gray-600 text-sm"
        />
        <button
          onClick={handleSendCommand}
          className="w-full px-2 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          disabled={!selectedNodeId || !customCommand}
        >
          Invia a {selectedNode?.name || "nodo"}
        </button>
      </div>

      {raspDialogOpen && (
        <RaspberryDialog node={raspNode} open={raspDialogOpen} onClose={() => setRaspDialogOpen(false)} />
      )}
    </aside>
  );
}
