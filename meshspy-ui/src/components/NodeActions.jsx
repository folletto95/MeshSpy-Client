import { Terminal } from "lucide-react";

export default function NodeActions({ node }) {
  // Puoi estendere con ulteriori azioni o pulsanti
  const handleLog = () => {
    console.log(`[Debug] Nodo selezionato: ${node.name}`);
  };

  return (
    <div className="mt-1 flex gap-1 text-sm text-gray-300">
      <button
        title="Logga info nodo"
        onClick={(e) => {
          e.stopPropagation(); // Previene il click che attiva zoom/richiesta posizione
          handleLog();
        }}
        className="hover:text-white"
      >
        <Terminal className="w-4 h-4" />
      </button>
    </div>
  );
}
