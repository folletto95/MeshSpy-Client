import React, { createContext, useContext, useRef, useState } from "react";

const MapContext = createContext();

export function MapProvider({ children }) {
  const mapRef = useRef(null);           // riferimento alla mappa Leaflet
  const markersRef = useRef({});         // riferimento a tutti i marker
  const [isReady, setIsReady] = useState(false); // stato inizializzazione mappa
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  console.log("MapProvider isReady:", isReady);

  return (
    <MapContext.Provider
      value={{
        mapRef,
        markersRef,
        isReady,
        setIsReady,
        selectedNodeId,
        setSelectedNodeId,
      }}
    >
      {children}
    </MapContext.Provider>
  );
}

export function useMap() {
  return useContext(MapContext);
}
