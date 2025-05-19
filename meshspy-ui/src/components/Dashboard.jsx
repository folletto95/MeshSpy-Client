import { useMap } from "../lib/MapContext";

function StatCard({ label, value, color }) {
  const classes = {
    blue: "bg-blue-100 text-blue-800",
    green: "bg-green-100 text-green-800",
    red: "bg-red-100 text-red-800",
    gray: "bg-gray-100 text-gray-800",
  };

  return (
    <div className={`flex flex-col p-4 rounded shadow w-full ${classes[color] || classes.gray}`}>
      <span className="text-sm font-medium">{label}</span>
      <span className="text-2xl font-bold">{value}</span>
    </div>
  );
}

export default function Dashboard() {
  const { nodes, isLoading, isError } = useMap();

  if (isLoading) {
    return (
      <div className="text-sm text-gray-500">
        ⏳ Caricamento metriche rete mesh...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-red-600">
        ❌ Errore nel caricamento delle metriche
      </div>
    );
  }

  const total = nodes.length;
  const gps = nodes.filter(n => n.hasPosition).length;
  const offline = nodes.filter(n => n.raw?.online === false).length;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <StatCard label="Nodi totali" value={total} color="blue" />
      <StatCard label="Con posizione" value={gps} color="green" />
      <StatCard label="Offline" value={offline} color="red" />
    </div>
  );
}
