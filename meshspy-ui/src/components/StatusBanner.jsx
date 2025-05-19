import { useMap } from "../lib/MapContext";

export default function StatusBanner() {
  const { nodes, isLoading, isError } = useMap();

  if (isLoading) {
    return (
      <div className="bg-yellow-100 text-yellow-800 px-4 py-2 text-sm font-medium rounded">
        ⏳ Caricamento rete mesh in corso...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-100 text-red-800 px-4 py-2 text-sm font-medium rounded">
        ❌ Errore nella connessione alla rete mesh
      </div>
    );
  }

  const total = nodes.length;
  const withPosition = nodes.filter(n => n.hasPosition).length;

  if (total === 0) {
    return (
      <div className="bg-red-100 text-red-800 px-4 py-2 text-sm font-medium rounded">
        🔴 Nessun nodo rilevato — rete mesh offline
      </div>
    );
  }

  if (withPosition < total) {
    return (
      <div className="bg-yellow-100 text-yellow-800 px-4 py-2 text-sm font-medium rounded">
        🟡 {total} nodi rilevati, {withPosition} con posizione valida
      </div>
    );
  }

  return (
    <div className="bg-green-100 text-green-800 px-4 py-2 text-sm font-medium rounded">
      🟢 Rete mesh operativa — {total} nodi attivi
    </div>
  );
}
