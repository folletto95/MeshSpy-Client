import { useNodes } from "../lib/api";
import { useMapContext } from "../lib/MapContext";
import { Radio, MapPin, MapPinOff } from "lucide-react";
import { addLogLine } from "./LogViewer";

export default function Sidebar() {
  const { data: nodesData, error } = useNodes();
  const { mapRef, markersRef, isReady } = useMapContext();

  if (error) {
    return (
      <aside className="w-60 bg-gray-900 text-white p-4">
        <p className="text-red-400">Errore caricamento nodi</p>
      </aside>
    );
  }

  const nodes = nodesData
    ? Object.entries(nodesData).map(([id, info]) => {
        const payload = info.data?.data?.payload || {};
        const hasPos = !!(payload.latitude_i && payload.longitude_i);
        return {
          id,
          name: info.name ?? "(senza nome)",
          hasPos,
        };
      })
    : [];

  const handleClick = async (node) => {
    addLogLine(`🖱️ Click su ${node.name} (hasPos=${node.hasPos})`);

    if (!isReady || !mapRef.current) {
      addLogLine("⏳ Mappa non ancora pronta");
      return;
    }

    if (node.hasPos) {
      const marker = markersRef.current[String(node.id)];
      if (marker) {
        const latlng = marker.getLatLng();
        mapRef.current.setView(latlng, 14, { animate: true });
        marker.openPopup();
        addLogLine(`📍 Zoom su ${node.name}`);
      } else {
        addLogLine(`❌ Marker non trovato per ${node.name}`);
      }
    } else {
      try {
        addLogLine(`📡 Richiesta posizione per nodo ${node.id} (${node.name})`);
        await fetch("/request-location", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ node_id: node.id }),
        });
      } catch (err) {
        addLogLine(`❌ Errore richiesta posizione nodo ${node.id}: ${err.message}`);
      }
    }
  };

  return (
    <aside className="w-60 bg-gradient-to-b from-meshtastic to-gray-900 text-white flex flex-col shadow-lg">
      <div className="flex items-center gap-2 px-4 py-5 text-xl font-semibold drop-shadow">
        <Radio className="w-6 h-6" />
        MeshSpy
      </div>
      <nav className="mt-2 flex-1 overflow-auto space-y-1">
        {nodes.length === 0 ? (
          <div className="px-4 py-2 text-gray-400">Nessun nodo disponibile</div>
        ) : (
          nodes.map((n) => (
            <button
              key={n.id}
              onClick={() => handleClick(n)}
              className="w-full flex items-center justify-between px-4 py-2 hover:bg-gray-700 rounded text-left"
            >
              <span className="flex-1 truncate flex items-center gap-2 text-white">
                {n.hasPos ? (
                  <MapPin className="w-4 h-4 text-white drop-shadow" />
                ) : (
                  <MapPinOff className="w-4 h-4 text-white/30" />
                )}
                {n.name}
              </span>
              <span className="relative flex h-2 w-2 text-meshtastic">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-current" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-current" />
              </span>
            </button>
          ))
        )}
      </nav>
    </aside>
  );
}
