import { useEffect, useState, useRef } from "react";
import { openLogSocket } from "../lib/api";

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
  const logRef = useRef(null);

  useEffect(() => {
    appendLogLine = (line) =>
      setLines((prev) => [...prev.slice(-49), line]);

    const ws = openLogSocket((line) =>
      setLines((prev) => [...prev.slice(-49), line])
    );

    ws.onerror = (e) => {
      appendLogLine(`[client] errore WebSocket: ${e.message}`);
    };

    return () => {
      ws.close();
      appendLogLine = null;
    };
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [lines]);

  return (
    <section>
      <h2 className="text-lg font-semibold text-gray-600">Live Log</h2>
      <div
        ref={logRef}
        className="mt-2 p-4 bg-black text-green-400 rounded-xl h-48 overflow-y-auto font-mono text-sm"
      >
        {lines.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </section>
  );
}
