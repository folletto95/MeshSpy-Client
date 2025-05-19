import React, { createContext, useContext, useRef, useState, useEffect } from "react";
import { useNodes } from "../lib/api";

const MapContext = createContext();

export function MapProvider({ children }) {
  const mapRef = useRef(null);
  const markersRef = useRef({});
  const [isReady, setIsReady] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [nodes, setNodes] = useState([]);

  const { data: rawData, isLoading, isError } = useNodes();

  useEffect(() => {
    if (!rawData) return;

    console.log("🔍 rawData ricevuto:", rawData); // DEBUG

    const result = Object.entries(rawData).map(([id, info]) => {
      const payload = info.data?.payload ?? {};
      const latRaw = payload.latitude_i ?? info.data?.latitude;
      const lonRaw = payload.longitude_i ?? info.data?.longitude;

      const lat = latRaw != null ? latRaw / 1e7 : null;
      const lon = lonRaw != null ? lonRaw / 1e7 : null;

      return {
        id,
        name:
          payload.longname ||
          payload.shortname ||
          info.name ||
          info.data?.name ||
          id,
        latitude: lat,
        longitude: lon,
        hasPosition: lat !== null && lon !== null,
        raw: info,
      };
    });

    setNodes(result);
  }, [rawData]);

  return (
    <MapContext.Provider
      value={{
        mapRef,
        markersRef,
        isReady,
        setIsReady,
        selectedNodeId,
        setSelectedNodeId,
        nodes,
        isLoading,
        isError,
      }}
    >
      {children}
    </MapContext.Provider>
  );
}

export function useMap() {
  return useContext(MapContext);
}
