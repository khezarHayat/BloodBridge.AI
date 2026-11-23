import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Fix for default Leaflet icon paths in Vite bundles
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom icons
const redPin = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const bluePin = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export interface MapMarkerItem {
  id: string;
  lat: number;
  lng: number;
  title: string;
  subtitle?: string;
  type: 'request' | 'blood_bank' | 'donor';
  bloodGroup?: string;
  phone?: string;
}

interface MapProps {
  markers?: MapMarkerItem[];
  center?: [number, number];
  zoom?: number;
  height?: string;
}

export const Map: React.FC<MapProps> = ({
  markers = [],
  center = [34.0151, 71.5249], // Peshawar center
  zoom = 12,
  height = '420px',
}) => {
  return (
    <div style={{ height }} className="w-full rounded-xl overflow-hidden border border-slate-200 shadow-sm relative">
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={false}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {markers.map((m) => (
          <Marker
            key={m.id}
            position={[m.lat, m.lng]}
            icon={m.type === 'blood_bank' ? bluePin : redPin}
          >
            <Popup>
              <div className="p-1">
                <span
                  className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                    m.type === 'blood_bank' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'
                  }`}
                >
                  {m.type === 'blood_bank' ? 'Blood Bank' : 'Emergency Request'}
                </span>
                <h4 className="font-bold text-slate-900 text-sm mt-1">{m.title}</h4>
                {m.subtitle && <p className="text-xs text-slate-600 mt-0.5">{m.subtitle}</p>}
                {m.bloodGroup && (
                  <p className="text-xs font-semibold text-crimson-600 mt-1">
                    Group: <span className="font-mono">{m.bloodGroup}</span>
                  </p>
                )}
                {m.phone && <p className="text-xs text-slate-500 mt-1">Contact: {m.phone}</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};
