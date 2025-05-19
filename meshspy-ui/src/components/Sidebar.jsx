import React from "react";
import { useMap } from "../lib/MapContext";

export default function Sidebar() {
  const { nodes, selectedNodeId, setSelectedNodeId } = useMap();

  const handleClick = (node) => {
    setSelectedNodeId(node.id);
    if (!node.hasPosition) {
      console.log(`[client] 📡 Richiesta posizione per nodo ${node.id} (${node.name})`);
    } else {
      console.log(`[client] 🗺️ Zoom su ${node.name}`);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 w-64 h-full shadow-md flex flex-col p-4">
      <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
        Nodi disponibili
      </h2>
      {nodes && nodes.length > 0 ? (
        <ul className="overflow-y-auto">
          {nodes.map((node) => (
            <li
              key={node.id}
              onClick={() => handleClick(node)}
              className={`cursor-pointer p-2 rounded mb-1 hover:bg-gray-200 dark:hover:bg-gray-700 ${
                selectedNodeId === node.id ? "bg-gray-100 dark:bg-gray-700 font-bold" : ""
              }`}
            >
              {node.name}
              {node.hasPosition ? (
                <span className="ml-2 text-green-500">📍</span>
              ) : (
                <span className="ml-2 text-gray-400">❓</span>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500 dark:text-gray-400">Nessun nodo disponibile</p>
      )}
    </div>
  );
}
