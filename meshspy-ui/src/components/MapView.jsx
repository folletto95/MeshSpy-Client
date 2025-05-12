import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useNodes } from "../lib/api";
import { useMapContext } from "../lib/MapContext";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// Configura le icone Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function MapView() {
  const { data: rawNodes } = useNodes();
  const { mapRef, markersRef, setIsReady } = useMapContext();

  const fallbackPosition = [42.5, 12.5]; // Default: centro Italia

  if (!rawNodes) {
    return (
      <div className="h-80 flex items-center justify-center text-gray-400">
        Caricamento mappa…
      </div>
    );
  }

  const nodes = Object.entries(rawNodes)
    .map(([id, info]) => {
      const payload = info.data?.payload || {};
      const lat = payload.latitude_i ? payload.latitude_i / 1e7 : null;
      const lon = payload.longitude_i ? payload.longitude_i / 1e7 : null;
      return lat && lon ? { id, name: info.name, lat, lon } : null;
    })
    .filter(Boolean);

  const center = nodes.length
    ? [
        nodes.reduce((sum, n) => sum + n.lat, 0) / nodes.length,
        nodes.reduce((sum, n) => sum + n.lon, 0) / nodes.length,
      ]
    : fallbackPosition;

  return (
    <div className="h-80 rounded-2xl overflow-hidden shadow-lg ring-1 ring-black/5">
      <MapContainer
        center={center}
        zoom={6}
        className="h-full w-full"
        whenCreated={(mapInstance) => {
          mapRef.current = mapInstance;
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
            ref={(marker) => {
              if (marker && marker.getLatLng) {
                markersRef.current[n.id] = marker;
              }
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
