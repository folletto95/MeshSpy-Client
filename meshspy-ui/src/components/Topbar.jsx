import { Plus } from "lucide-react";

export default function Topbar() {
  return (
    <header className="flex items-center justify-between bg-white border-b px-6 py-3 shadow">
      <h1 className="text-xl font-semibold text-gray-700">MeshSpy</h1>
      <button className="flex items-center gap-2 px-4 py-2 text-sm bg-meshtastic text-white rounded hover:bg-green-600">
        <Plus className="w-4 h-4" />
        Aggiungi Nodo
      </button>
    </header>
  );
}
