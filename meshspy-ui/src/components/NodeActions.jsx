import { Terminal, Info, Send } from "lucide-react";
import { addLogLine } from "./LogViewer";

export default function NodeActions({ node }) {
  const handleLog = () => {
    console.log("[Debug Node]", node);
    addLogLine(`🖥️ Debug in console per ${node.name}`);
  };

  const handleDetails = () => {
    const info = JSON.stringify(node.data || {}, null, 2);
    alert(`📄 Dettagli nodo ${node.name}:\n\n${info}`);
  };

  const handleCommand = () => {
    // Puoi inviare comandi via API al backend se previsto
    addLogLine(`🔧 Comando custom inviato a ${node.name}`);
    // TODO: integrare invio via fetch se esiste endpoint
  };

  return (
    <div className="mt-1 flex gap-2 text-sm text-gray-300">
      <button
        title="Dettagli nodo"
        onClick={(e) => {
          e.stopPropagation();
          handleDetails();
        }}
        className="hover:text-white"
      >
        <Info className="w-4 h-4" />
      </button>

      <button
        title="Comando custom"
        onClick={(e) => {
          e.stopPropagation();
          handleCommand();
        }}
        className="hover:text-white"
      >
        <Send className="w-4 h-4" />
      </button>

      <button
        title="Debug console"
        onClick={(e) => {
          e.stopPropagation();
          handleLog();
        }}
        className="hover:text-white"
      >
        <Terminal className="w-4 h-4" />
      </button>
    </div>
  );
}
