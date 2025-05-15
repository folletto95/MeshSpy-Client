import { RadioTower, Activity, Clock } from "lucide-react";
import { useNodes } from "../lib/api";

const metricStyle =
  "flex items-center gap-3 p-5 bg-white rounded-2xl shadow hover:shadow-md";

export default function Metrics() {
  const { nodes, isLoading, isError } = useNodes();

  if (isError) return <p className="text-red-500">Errore caricamento nodi</p>;
  if (isLoading) return <p className="text-gray-500">Caricamento nodi…</p>;

  const total = Object.keys(nodes).length;
  const online = total; // da aggiornare con logica corretta

  return (
    <section className="grid sm:grid-cols-3 gap-4 my-4">
      <div className={metricStyle}>
        <RadioTower className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Nodi Online</p>
          <p className="text-xl font-bold">{online} / {total}</p>
        </div>
      </div>
      <div className={metricStyle}>
        <Activity className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Messaggi Totali</p>
          <p className="text-xl font-bold">—</p>
        </div>
      </div>
      <div className={metricStyle}>
        <Clock className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Uptime Medio</p>
          <p className="text-xl font-bold">—</p>
        </div>
      </div>
    </section>
  );
}
