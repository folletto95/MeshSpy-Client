// src/components/Topbar.jsx
export default function Topbar() {
  return (
    <header className="h-12 px-4 flex items-center justify-between bg-white/70 backdrop-blur sticky top-0 z-10 shadow">
      <span className="text-sm text-gray-700">Broker: online</span>
      <button className="px-3 py-1 rounded-lg bg-meshtastic hover:bg-meshtastic/90 text-white text-sm shadow">
        Add Node
      </button>
    </header>
  );
}
