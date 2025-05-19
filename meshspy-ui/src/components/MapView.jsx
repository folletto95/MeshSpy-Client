import React, { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useMap } from "../lib/MapContext";
import { createNodeMarker } from "../lib/markerIcons";


export default function MapView() {
  const { mapRef, markersRef, nodes, isReady, setIsReady, selectedNodeId } = useMap();

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map").setView([43.7167, 10.4000], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(mapRef.current);
      setIsReady(true);
    }
  }, []);

  useEffect(() => {
    if (!isReady) return;

    nodes.forEach((node) => {
      const marker = markersRef.current[node.id];

      if (node.hasPosition && node.latitude != null && node.longitude != null) {
        const latLng = [node.latitude, node.longitude];

        if (!marker) {
        const newMarker = L.marker(latLng, {
          icon: createNodeMarker({
            color: node.id === selectedNodeId ? "#3399FF" : "#00CC66",
            emoji: "📡"
          })
        })
          markersRef.current[node.id] = newMarker;
        } else {
          marker.setLatLng(latLng);
        }
      } else {
        // se non ha posizione, rimuovi il marker se esiste
        if (marker) {
          mapRef.current.removeLayer(marker);
          delete markersRef.current[node.id];
        }
      }
    });
  }, [nodes, isReady]);

  useEffect(() => {
    if (!isReady || !selectedNodeId) return;

    const marker = markersRef.current[selectedNodeId];
    if (marker) {
      marker.openPopup();
      mapRef.current.flyTo(marker.getLatLng(), 17);
    } else {
      console.log(`[client] ❌ Marker non trovato per ${selectedNodeId}`);
    }
  }, [selectedNodeId, isReady]);

  return <div id="map" className="h-full w-full" />;
}
