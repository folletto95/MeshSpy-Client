import useSWR from "swr";

// Try env var first; if undefined, fall back to window.location (host + port 8000)
const API =
  import.meta.env.VITE_API ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

export const fetcher = (url) =>
  fetch(API + url).then((r) => {
    if (!r.ok) throw new Error(`Fetch error ${r.status} for ${API + url}`);
    return r.json();
  });

export function useNodes() {
  return useSWR("/nodes", fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });
}

export function useMetrics() {
  return useSWR("/metrics", fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  });
}

export function openLogSocket(onLine) {
  const wsUrl = `${API.replace(/^http/, "ws")}/ws/logs`;
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (e) => onLine(e.data);
  return ws;
}

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
