import { createContext, useContext, useEffect, useRef, useState } from "react";
import { fetchNodes } from "../lib/api";

const MapContext = createContext();

export const MapProvider = ({ children }) => {
  const [nodes, setNodes] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const mapRef = useRef(null);
  const markersRef = useRef({});
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const loadNodes = async () => {
      try {
        const data = await fetchNodes();
        const processed = Object.entries(data).map(([id, entry]) => {
          const d = entry.data;
          let lat = d?.latitude ?? d?.payload?.latitude_i / 1e7;
          let lon = d?.longitude ?? d?.payload?.longitude_i / 1e7;
          return {
            id,
            name: d?.payload?.longname || entry.name || id,
            latitude: lat,
            longitude: lon,
            hasPosition: lat != null && lon != null,
          };
        });
        setNodes(processed);
      } catch (error) {
        console.error("Errore caricamento nodi:", error);
      }
    };

    loadNodes();
  }, []);

  return (
    <MapContext.Provider
      value={{
        nodes,
        setNodes,
        selectedNodeId,
        setSelectedNodeId,
        mapRef,
        markersRef,
        isReady,
        setIsReady,
      }}
    >
      {children}
    </MapContext.Provider>
  );
};

export const useMap = () => useContext(MapContext);
