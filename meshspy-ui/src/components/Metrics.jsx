import { RadioTower, Activity, Clock } from "lucide-react";
import { useNodes } from "../lib/api";

const boxStyle =
  "flex items-center gap-3 p-5 bg-white rounded-2xl shadow hover:shadow-md transition";

export default function Metrics() {
  const { nodes, isLoading, isError } = useNodes();

  if (isError)
    return <div className="text-red-500 mb-4">Errore caricamento nodi</div>;

  if (isLoading)
    return <div className="text-gray-500 mb-4">Caricamento metriche…</div>;

  const total = Object.keys(nodes).length;
  const online = total; // TODO: sostituire con logica reale

  return (
    <section className="grid sm:grid-cols-3 gap-4 mb-4">
      <div className={boxStyle}>
        <RadioTower className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Nodi online</p>
          <p className="text-xl font-bold">
            {online} / {total}
          </p>
        </div>
      </div>
      <div className={boxStyle}>
        <Activity className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Messaggi totali</p>
          <p className="text-xl font-bold">—</p>
        </div>
      </div>
      <div className={boxStyle}>
        <Clock className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Uptime medio</p>
          <p className="text-xl font-bold">—</p>
        </div>
      </div>
    </section>
  );
}
