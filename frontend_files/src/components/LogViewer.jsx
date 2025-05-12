// src/components/LogViewer.jsx
import { useState, useEffect, useRef } from "react";

const mockLines = [
  "[11:24:00] NODE‑01 → Hello world!",
  "[11:24:05] NODE‑03 → Ack",
];

export default function LogViewer() {
  const [lines, setLines] = useState(mockLines);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="rounded-2xl shadow-md ring-1 ring-black/5 overflow-hidden">
      <div className="bg-gray-800 text-meshtastic px-4 py-1 text-xs font-semibold">
        Live Log
      </div>
      <div className="bg-black text-green-400 p-4 h-48 overflow-auto font-mono text-sm">
        {lines.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
