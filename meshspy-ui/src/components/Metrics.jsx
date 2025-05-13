import { RadioTower, Activity, Clock } from "lucide-react";
import { useNodes } from "../lib/api";

const metricStyle =
  "flex items-center gap-3 p-5 bg-white rounded-2xl shadow-md hover:shadow-lg transition";

export default function Metrics() {
  const { data: nodesData, error } = useNodes();

  if (error) return <p className="text-red-500">Errore nel caricamento dei nodi</p>;
  if (!nodesData) return <p>Caricamento in corso…</p>;

  const nodes = Object.entries(nodesData).map(([id, info]) => ({
    id,
    ...info,
  }));

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

      {/* Messaggi totali */}
      <div className={metricStyle}>
        <Activity className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Messaggi totali</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
      </div>

      {/* Uptime medio */}
      <div className={metricStyle}>
        <Clock className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Uptime medio</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
      </div>
    </section>
  );
}
