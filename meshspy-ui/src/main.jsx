import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import { MapProvider } from "./lib/MapContext.jsx";

// (Facoltativo) Carica preferenza dark mode da localStorage
if (localStorage.theme === "dark") {
  document.documentElement.classList.add("dark");
} else {
  document.documentElement.classList.remove("dark");
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MapProvider>
      <App />
    </MapProvider>
  </React.StrictMode>
);