// src/components/MapView.jsx
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const nodes = [
  { id: "NODE-01", pos: [45.07, 9.65] },
  { id: "NODE-03", pos: [44.35, 10.99] },
];

export default function MapView() {
  return (
    <div className="h-80 rounded-2xl overflow-hidden shadow-lg ring-1 ring-black/5">
      <MapContainer
        center={[45.0, 9.0]}
        zoom={6}
        className="h-full w-full"
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {nodes.map((n) => (
          <Marker key={n.id} position={n.pos}>
            <Popup>{n.id}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
