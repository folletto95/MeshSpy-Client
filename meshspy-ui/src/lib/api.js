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

//
const fetcher = (url) => fetch(url).then((res) => res.json());

// Hook per ottenere la lista dei nodi
export function useNodes() {
  const { data, error } = useSWR("/api/nodes", fetcher, {
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
