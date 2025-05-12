import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/nodes": "http://localhost:8000",
      "/metrics": "http://localhost:8000",
      "/request-location": "http://localhost:8000",
      "/wifi-config": "http://localhost:8000",
      "^/ws/.*": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
