// meshspy-ui/src/lib/MapContext.jsx
import { createContext, useContext, useRef, useState } from "react";

const MapContext = createContext(null);

export function MapProvider({ children }) {
  const mapRef = useRef(null);
  const markersRef = useRef({});
  const [isReady, setIsReady] = useState(false);
  console.log("MapProvider isReady:", isReady);

  return (
    <MapContext.Provider value={{ mapRef, markersRef, isReady, setIsReady }}>
      {children}
    </MapContext.Provider>
  );
}

export function useMapContext() {
  const ctx = useContext(MapContext);
  if (!ctx) throw new Error("useMapContext must be used inside MapProvider");
  return ctx;
}
