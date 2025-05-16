import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useMap } from "../lib/MapContext";
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
  const { nodes, mapRef, markersRef, setIsReady } = useMap();

  const nodesWithPos = nodes.filter((n) => n.hasPosition);

  const fallbackCenter = [43.7162, 10.4017];
  const center =
    nodesWithPos.length > 0
      ? [
          nodesWithPos.reduce((sum, n) => sum + n.latitude, 0) /
            nodesWithPos.length,
          nodesWithPos.reduce((sum, n) => sum + n.longitude, 0) /
            nodesWithPos.length,
        ]
      : fallbackCenter;

  return (
    <div className="h-80 rounded-2xl overflow-hidden shadow ring-1 ring-black/5">
      <MapContainer
        center={center}
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
        {nodesWithPos.map((n) => (
          <Marker
            key={n.id}
            position={[n.latitude, n.longitude]}
            ref={(el) => {
              if (el) markersRef.current[n.id] = el;
            }}
          >
            <Popup>
              <div className="font-semibold">{n.name}</div>
              <div className="text-sm text-gray-500">
                {n.latitude.toFixed(5)}, {n.longitude.toFixed(5)}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
