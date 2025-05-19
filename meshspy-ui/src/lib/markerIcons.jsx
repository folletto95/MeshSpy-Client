// src/lib/markerIcons.jsx
import L from "leaflet";

export function createNodeMarker({ color = "#00CC66", emoji = "📡", size = 32 }) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">
      <circle cx="${size / 2}" cy="${size / 2}" r="${(size / 2) - 2}" fill="${color}" stroke="white" stroke-width="2" />
      <text x="50%" y="60%" text-anchor="middle" fill="white" font-size="14" font-family="sans-serif">${emoji}</text>
    </svg>
  `;

  return L.divIcon({
    className: "",
    html: svg,
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size / 2]
  });
}
