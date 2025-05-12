// meshspy-ui/src/components/Metrics.jsx
import { RadioTower, Activity, Clock } from "lucide-react";
import { useNodes } from "../lib/api";

const metricStyle =
  "flex items-center gap-3 p-5 bg-white rounded-2xl shadow-md hover:shadow-lg transition";

export default function Metrics() {
  // Prendiamo i dati raw (un oggetto { nodeId: { … } })
  const { data: nodesData, error } = useNodes();

  // Se c’è un errore o non ci sono dati, rimaniamo a vuoto
  if (error) return <p className="text-red-500">Errore nel caricamento dei nodi</p>;
  if (!nodesData) return <p>Caricamento in corso…</p>;

  // Convertiamo l’oggetto in un array di nodi
  const nodes = Object.entries(nodesData).map(([id, info]) => ({
    id,
    ...info,
  }));

  // Ora possiamo filtrare e contare
  const totalCount = nodes.length;
  const onlineCount = nodes.filter((n) => n.online).length;

  return (
    <section className="grid sm:grid-cols-3 gap-4">
      {/* Nodi online */}
      <div className={metricStyle}>
        <RadioTower className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Nodi online</p>
          <p className="text-2xl font-semibold">
            {onlineCount} / {totalCount}
          </p>
        </div>
      </div>

      {/* Messaggi totali (sempre dinamico, se hai un endpoint /metrics) */}
      <div className={metricStyle}>
        <Activity className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Messaggi totali</p>
          {/* Se usi useMetrics(), sostituisci con il dato reale */}
          <p className="text-2xl font-semibold">—</p>
        </div>
      </div>

      {/* Uptime medio (idem) */}
      <div className={metricStyle}>
        <Clock className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Uptime medio</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
      </div>
    </section>
  );
}import { useMetrics } from "../lib/api";

export default function Metrics() {
  const { data } = useMetrics();

  if (!data) {
    return (
      <section className="bg-white rounded-xl p-4 shadow">
        <p className="text-gray-400">Caricamento metriche...</p>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-xl p-4 shadow">
      <h2 className="text-lg font-semibold text-gray-600 mb-2">Metriche</h2>
      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
        {JSON.stringify(data, null, 2)}
      </pre>
    </section>
  );
}
