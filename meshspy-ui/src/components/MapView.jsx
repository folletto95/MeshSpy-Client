import React, { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useMap } from "../lib/MapContext";

export default function MapView() {
  const { mapRef, markersRef, nodes, isReady, setIsReady, selectedNodeId } = useMap();

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map").setView([43.7167, 10.4], 12);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(mapRef.current);
      setIsReady(true);
    }
  }, []);

  useEffect(() => {
    if (!isReady) return;

    nodes.forEach((node) => {
      const existing = markersRef.current[node.id];

      if (node.hasPosition) {
        const latlng = [node.latitude, node.longitude];
        if (!existing) {
          const m = L.marker(latlng).addTo(mapRef.current).bindPopup(node.name);
          markersRef.current[node.id] = m;
        } else {
          existing.setLatLng(latlng);
        }
      } else if (existing) {
        mapRef.current.removeLayer(existing);
        delete markersRef.current[node.id];
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
