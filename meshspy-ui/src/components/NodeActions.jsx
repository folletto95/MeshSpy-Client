import { requestNodePosition } from "../lib/api";

export default function NodeActions({ node }) {
  if (!node) return null;

  return (
    <div className="space-y-2 mt-2">
      <button
        onClick={() => requestNodePosition(node.id)}
        className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
      >
        📍 Richiedi posizione
      </button>
    </div>
  );
}
