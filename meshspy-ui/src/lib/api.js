import useSWR from "swr";

// Usa variabile d'ambiente o fallback su localhost:8000
const API =
  import.meta.env.VITE_API ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

// Fetcher comune per tutte le API
export const fetcher = (url) =>
  fetch(API + url).then((r) => {
    if (!r.ok) throw new Error(`Fetch error ${r.status} for ${API + url}`);
    return r.json();
  });

// Hook per ottenere la lista dei nodi
export function useNodes() {
  const { data, error } = useSWR("/nodes", fetcher, {
    refreshInterval: 5000,
  });

  return {
    nodes: data || {},
    isLoading: !error && !data,
    isError: error,
  };
}

// Hook per ottenere metriche (se supportate)
export function useMetrics() {
  return useSWR("/metrics", fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });
}

// WebSocket logs
export function openLogSocket(onLine) {
  const API =
    import.meta.env.VITE_API ||
    `${window.location.protocol}//${window.location.hostname}:8000`;
  const wsUrl = `${API.replace(/^http/, "ws")}/ws/logs`;
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (e) => onLine(e.data);
  return ws;
}

// Post per creare wifi.yaml
export async function createWifiYaml(data) {
  const res = await fetch(API + "/wifi-config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok)
    throw new Error(`Fetch error ${res.status} for ${API}/wifi-config`);
  return res.json();
}

// Richiede la posizione da un nodo specifico
export async function requestNodePosition(node_id) {
  const res = await fetch(API + "/request-position", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ node_id }),
  });
  if (!res.ok)
    throw new Error(`Fetch error ${res.status} for ${API}/request-position`);
  return res.json();
}


export async function sendCustomCommand(node_id, command) {
  const res = await fetch(API + "/send-command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ node_id, command }),
  });
  if (!res.ok) throw new Error("Errore invio comando");
  return res.json();
}


export async function sendUpdate(node_id) {
  const res = await fetch(API + `/berry/${node_id}/update`, { method: "POST" });
  if (!res.ok) throw new Error("Errore update");
  return res.json();
}

export async function sendReboot(node_id) {
  const res = await fetch(API + `/berry/${node_id}/reboot`, { method: "POST" });
  if (!res.ok) throw new Error("Errore reboot");
  return res.json();
}

export async function setManualPosition(node_id, lat, lng) {
  const res = await fetch(API + `/berry/${node_id}/set-position`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lat, lng }),
  });
  if (!res.ok) throw new Error("Errore invio posizione");
  return res.json();
}
