import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // In produzione non serve il dev‐server proxy:
  // lasciamo che il reverse-proxy (Nginx, Caddy, ecc.) gestisca /nodes, /metrics, /ws.
  //
  // SE vuoi ancora sviluppare con Vite e proxy, decommenta qui sotto:
  //
  // server: {
  //   host: true,           // ascolta su 0.0.0.0
  //   port: 5173,
  //   allowedHosts: "all",
  //   proxy: {
  //     "/nodes": {
  //       target: "http://localhost:8000",
  //       changeOrigin: true,
  //     },
  //     "/metrics": {
  //       target: "http://localhost:8000",
  //       changeOrigin: true,
  //     },
  //     "/ws": {
  //       target: "ws://localhost:8000",
  //       ws: true,
  //     },
  //   },
  // },
});
