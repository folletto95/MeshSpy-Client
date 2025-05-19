import { useMap } from "../lib/MapContext";
import { Radio, MapPin, HelpCircle } from "lucide-react";
import { addLogLine } from "./LogViewer";
import { requestNodePosition } from "../lib/api";
import NodeActions from "./NodeActions";

export default function Sidebar() {
  const { nodes, mapRef, markersRef } = useMap();

  const handleClick = async (node) => {
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

  return (
    <aside className="w-64 h-full bg-gradient-to-b from-meshtastic to-gray-900 dark:from-gray-800 dark:to-gray-900 text-white shadow-md flex flex-col">
      <div className="flex items-center gap-2 px-4 py-5 text-xl font-semibold drop-shadow">
        <Radio className="w-6 h-6" />
        MeshSpy
      </div>
      <nav className="mt-2 flex-1 overflow-auto space-y-1">
        {nodes.length === 0 ? (
          <div className="px-4 py-2 text-gray-400">
            Nessun nodo disponibile
          </div>
        ) : (
          nodes.map((n) => (
            <div
              key={n.id}
              className="flex items-center justify-between px-4 py-2 hover:bg-gray-700 rounded cursor-pointer"
              onClick={() => handleClick(n)}
            >
              <div className="flex-1 truncate">
                <div className="flex items-center gap-2">
                  {n.hasPosition ? (
                    <MapPin className="w-4 h-4 text-lime-400" />
                  ) : (
                    <HelpCircle className="w-4 h-4 text-gray-400" />
                  )}
                  {n.name}
                </div>
                <NodeActions node={n} />
              </div>
            </div>
          ))
        )}
      </nav>
    </aside>
  );
}
