import { useNodes } from "../lib/api";
import { useMapContext } from "../lib/MapContext";
import { Radio, MapPin, HelpCircle } from "lucide-react";
import { addLogLine } from "./LogViewer";

export default function Sidebar() {
  const { data: nodesData, error } = useNodes();
  const { mapRef, markersRef } = useMapContext();

  if (error) {
    return (
      <aside className="w-60 bg-gray-900 text-white p-4">
        <p className="text-red-400">Errore caricamento nodi</p>
      </aside>
    );
  }

  const nodes = nodesData
    ? Object.entries(nodesData).map(([id, info]) => {
        const payload = info.data?.payload || {};
        const hasPos = !!(payload.latitude_i && payload.longitude_i);
        return {
          id,
          name: info.name ?? "(senza nome)",
          hasPos,
        };
      })
    : [];

  const handleClick = async (node) => {
    if (node.hasPos) {
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
        await fetch(`/request-location/${node.id}`, { method: "POST" });
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
          <div className="px-4 py-2 text-gray-400">Nessun nodo disponibile</div>
        ) : (
          nodes.map((n) => (
            <div
              key={n.id}
              className="flex items-center justify-between px-4 py-2 hover:bg-gray-700 rounded cursor-pointer"
              onClick={() => handleClick(n)}
            >
              <span className="flex-1 truncate flex items-center gap-2">
                {n.hasPos ? (
                  <MapPin className="w-4 h-4 text-lime-400" />
                ) : (
                  <HelpCircle className="w-4 h-4 text-gray-400" />
                )}
                {n.name}
              </span>
            </div>
          ))
        )}
      </nav>
    </aside>
  );
}
