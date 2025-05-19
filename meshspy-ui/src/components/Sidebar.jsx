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

  if (!nodes || nodes.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 p-4 shadow h-full w-64">
        <p className="text-gray-500">Nessun nodo disponibile</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-4 shadow h-full w-64 overflow-y-auto">
      <h2 className="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-200">Nodi</h2>
      <ul>
        {nodes.map((node) => (
          <li
            key={node.id}
            onClick={() => handleClick(node)}
            className={`cursor-pointer p-2 rounded mb-1 hover:bg-gray-200 dark:hover:bg-gray-700 ${
              selectedNodeId === node.id ? "bg-gray-100 dark:bg-gray-700 font-bold" : ""
            }`}
          >
            <span>{node.name}</span>
            {node.hasPosition ? (
              <span className="ml-2 text-green-500">📍</span>
            ) : (
              <span className="ml-2 text-gray-400">❓</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
