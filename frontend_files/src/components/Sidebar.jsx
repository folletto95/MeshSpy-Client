// src/components/Sidebar.jsx
import { Radio } from "lucide-react";

const mockNodes = [
  { id: "NODE-01", name: "Nodo‑01", online: true },
  { id: "NODE-02", name: "Nodo‑02", online: false },
  { id: "NODE-03", name: "Nodo‑03", online: true },
];

export default function Sidebar() {
  return (
    <aside className="w-60 bg-gradient-to-b from-meshtastic to-gray-900 text-white flex flex-col shadow-lg">
      <div className="flex items-center gap-2 px-4 py-5 text-xl font-semibold drop-shadow">
        <Radio className="w-6 h-6" />
        MeshSpy
      </div>

      <nav className="flex-1 px-2 space-y-1">
        {mockNodes.map((n) => (
          <div
            key={n.id}
            className={`flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white/5 transition ${
              n.online ? "bg-white/10" : "opacity-40"
            }`}
          >
            <span>{n.name}</span>
            <span
              className={`relative flex h-2 w-2 ${
                n.online ? "text-meshtastic" : "text-red-500"
              }`}
            >
              {n.online && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-current"></span>
              )}
              <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
            </span>
          </div>
        ))}
      </nav>
    </aside>
  );
}
