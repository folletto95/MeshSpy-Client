import { useEffect, useState } from "react";
import { openLogSocket } from "../lib/api";

// funzione per log client-side esportabile
let appendLogLine = null;

export function addLogLine(line) {
  if (appendLogLine) {
    appendLogLine(`[client] ${line}`);
  } else {
    console.log("[log]", line);
  }
}

export default function LogViewer() {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    appendLogLine = (line) => {
      setLines((prev) => [...prev.slice(-49), line]);
    };

    const ws = openLogSocket((line) => {
      setLines((prev) => [...prev.slice(-49), line]);
    });

    return () => {
      ws.close();
      appendLogLine = null;
    };
  }, []);

  return (
    <section>
      <h2 className="text-lg font-semibold text-gray-600">Live Log</h2>
      <div className="mt-2 p-4 bg-black text-green-400 rounded-xl h-48 overflow-y-auto font-mono text-sm">
        {lines.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </section>
  );
}
