import { Plus, Moon, Sun } from "lucide-react";
import useDarkMode from "../hooks/useDarkMode";

export default function Topbar() {
  const [darkMode, setDarkMode] = useDarkMode();

  return (
    <header className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-900 border-b dark:border-gray-700 shadow">
      <h1 className="text-xl font-semibold text-gray-700 dark:text-white">MeshSpy</h1>
      <div className="flex items-center gap-4">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="text-gray-700 dark:text-white hover:text-meshtastic dark:hover:text-meshtastic transition"
          title="Toggle Dark Mode"
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-sm bg-meshtastic text-white rounded hover:bg-green-600">
          <Plus className="w-4 h-4" />
          Aggiungi Nodo
        </button>
      </div>
    </header>
  );
}