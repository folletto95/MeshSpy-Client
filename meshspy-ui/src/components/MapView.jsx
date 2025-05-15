import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useNodes } from "../lib/api";
import { useMapContext } from "../lib/MapContext";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function MapView() {
  const { data: nodesData } = useNodes();
  const { mapRef, markersRef, setIsReady } = useMapContext();

  const nodes = nodesData
    ? Object.entries(nodesData)
        .map(([id, info]) => {
          const payload = info.data?.payload;
          if (!payload?.latitude_i || !payload?.longitude_i) return null;

          return {
            id,
            name: info.name,
            lat: payload.latitude_i / 1e7,
            lon: payload.longitude_i / 1e7,
          };
        })
        .filter(Boolean)
    : [];

  if (nodes.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-gray-400">
        Caricamento mappa…
      </div>
    );
  }

  const avgLat = nodes.reduce((sum, n) => sum + n.lat, 0) / nodes.length;
  const avgLon = nodes.reduce((sum, n) => sum + n.lon, 0) / nodes.length;

  return (
    <div className="h-80 rounded-2xl overflow-hidden shadow ring-1 ring-black/5">
      <MapContainer
        center={[avgLat, avgLon]}
        zoom={6}
        className="h-full w-full"
        whenCreated={(map) => {
          mapRef.current = map;
          setIsReady(true);
        }}
      >
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {nodes.map((n) => (
          <Marker
            key={n.id}
            position={[n.lat, n.lon]}
            ref={(el) => {
              if (el) markersRef.current[n.id] = el;
            }}
          >
            <Popup>
              <div className="font-semibold">{n.name}</div>
              <div className="text-sm text-gray-500">
                {n.lat.toFixed(5)}, {n.lon.toFixed(5)}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
