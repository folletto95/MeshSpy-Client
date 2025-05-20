import { useState } from "react";
import { Dialog } from "@headlessui/react";
import { sendReboot, sendUpdate, setManualPosition } from "../lib/api";

export default function RaspberryDialog({ node, open, onClose }) {
  const [tab, setTab] = useState("position");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpdate = async () => {
    setLoading(true);
    try {
      await sendUpdate(node.id);
      alert("✅ Aggiornamento avviato");
    } catch (err) {
      alert("❌ Errore aggiornamento");
    }
    setLoading(false);
  };

  const handleReboot = async () => {
    setLoading(true);
    try {
      await sendReboot(node.id);
      alert("🔁 Nodo riavviato");
    } catch (err) {
      alert("❌ Errore reboot");
    }
    setLoading(false);
  };

  const handleSetPosition = async () => {
    if (!lat || !lng) return;
    setLoading(true);
    try {
      await setManualPosition(node.id, lat, lng);
      alert("📍 Posizione inviata");
    } catch (err) {
      alert("❌ Errore invio posizione");
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onClose={onClose} className="fixed z-10 inset-0">
      <div className="fixed inset-0 bg-black/50" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white dark:bg-gray-800 text-black dark:text-white rounded p-6 max-w-md w-full space-y-4">
          <Dialog.Title className="text-lg font-bold">🍓 Raspberry: {node.name}</Dialog.Title>

          <div className="flex gap-2 border-b pb-2 text-sm">
            <button onClick={() => setTab("position")} className={tab === "position" ? "font-semibold underline" : ""}>📍 Posizione</button>
            <button onClick={() => setTab("update")} className={tab === "update" ? "font-semibold underline" : ""}>⬇️ Update</button>
            <button onClick={() => setTab("reboot")} className={tab === "reboot" ? "font-semibold underline" : ""}>🔁 Riavvio</button>
          </div>

          {tab === "position" && (
            <div className="space-y-2">
              <label>Latitudine</label>
              <input className="w-full px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded" value={lat} onChange={(e) => setLat(e.target.value)} />
              <label>Longitudine</label>
              <input className="w-full px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded" value={lng} onChange={(e) => setLng(e.target.value)} />
              <button disabled={loading} onClick={handleSetPosition} className="bg-blue-600 text-white px-4 py-1 rounded w-full">📡 Invia posizione</button>
            </div>
          )}

          {tab === "update" && (
            <div>
              <p>Invia comando di aggiornamento software alla Raspberry.</p>
              <button disabled={loading} onClick={handleUpdate} className="mt-2 bg-orange-500 text-white px-4 py-1 rounded w-full">⬇️ Avvia Update</button>
            </div>
          )}

          {tab === "reboot" && (
            <div>
              <p>Riavvia il nodo remoto collegato alla Raspberry.</p>
              <button disabled={loading} onClick={handleReboot} className="mt-2 bg-red-600 text-white px-4 py-1 rounded w-full">🔁 Riavvia</button>
            </div>
          )}

          <div className="text-right text-sm pt-4">
            <button onClick={onClose} className="underline">Chiudi</button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}
