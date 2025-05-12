// src/components/Metrics.jsx
import { RadioTower } from "lucide-react";
import { useMetrics } from "../lib/api";

export default function Metrics() {
  const { data } = useMetrics();

  return (
    <section className="grid sm:grid-cols-1 gap-4">
      <div className="flex items-center gap-3 p-5 bg-white rounded-2xl shadow">
        <RadioTower className="text-meshtastic" />
        <div>
          <p className="text-sm text-gray-500">Nodi online</p>
          <p className="text-2xl font-semibold">
            {data ? `${data.online} / ${data.total}` : "--"}
          </p>
        </div>
      </div>
    </section>
  );
}
