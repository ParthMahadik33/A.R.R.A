import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet container sizing
const mapContainerStyle = {
  width: '100%',
  height: '100%',
  background: '#111'
};

export default function RailwayMap({ stations, trains, activeIncident, signalStates }) {
  const [mapCenter, setMapCenter] = useState([18.5, 82.5]); // Centered in Odisha/AP region of corridor
  const [mapZoom, setMapZoom] = useState(6);

  // Focus map on incident when triggered
  useEffect(() => {
    if (activeIncident && activeIncident.location) {
      setMapCenter([activeIncident.location.lat, activeIncident.location.lng]);
      setMapZoom(9);
    }
  }, [activeIncident]);

  // Create tracks: connect all sorted stations
  const sortedStations = [...stations].sort((a, b) => a.km - b.km);
  const trackPositions = sortedStations.map(s => [s.lat, s.lng]);

  // Dynamic Custom HTML Marker Icons using Leaflet divIcon
  const createStationIcon = (stationCode) => {
    const isIncidentStation = activeIncident && activeIncident.nearest_station_code === stationCode;
    
    return L.divIcon({
      className: 'custom-station-icon',
      html: `
        <div class="flex flex-col items-center">
          <div class="w-3 h-3 rounded-full border border-gray-400 bg-gray-800 shadow-[0_0_8px_rgba(255,255,255,0.4)] ${isIncidentStation ? 'animate-ping bg-yellow-500 border-yellow-300' : ''}"></div>
          <span class="text-[9px] font-semibold text-gray-400 mt-1 uppercase tracking-tight font-mono bg-black/80 px-1 py-[1px] rounded border border-gray-900">${stationCode}</span>
        </div>
      `,
      iconSize: [40, 30],
      iconAnchor: [20, 15]
    });
  };

  const createTrainIcon = (train) => {
    const isUp = train.direction === 'UP';
    const isHalted = train.status === 'HALTED' || train.speed === 0;
    const isHalting = train.status === 'HALTING';
    
    // Choose neon color based on status and direction
    let colorClass = isUp ? 'bg-cyan-500 shadow-cyan-500/80' : 'bg-fuchsia-500 shadow-fuchsia-500/80';
    if (isHalted) {
      colorClass = 'bg-red-600 shadow-red-600/100 animate-pulse';
    } else if (isHalting) {
      colorClass = 'bg-yellow-500 shadow-yellow-500/80 animate-ping';
    }

    return L.divIcon({
      className: 'custom-train-icon',
      html: `
        <div class="relative flex items-center justify-center">
          <!-- Pulse animation for running/braking trains -->
          ${!isHalted ? `<div class="absolute w-6 h-6 rounded-full border border-current opacity-30 animate-ping ${isUp ? 'text-cyan-400' : 'text-fuchsia-400'}"></div>` : ''}
          <div class="w-4.5 h-4.5 rounded-full ${colorClass} flex items-center justify-center border border-black shadow-[0_0_12px_2px_rgba(0,0,0,0.5)]">
            <span class="text-[8px] text-white font-extrabold font-mono">${isUp ? '↑' : '↓'}</span>
          </div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  };

  const createSignalIcon = (sig) => {
    const isRed = sig.color === 'RED';
    return L.divIcon({
      className: 'custom-signal-icon',
      html: `
        <div class="w-3 h-3 rounded-full border border-black ${isRed ? 'bg-red-600 shadow-[0_0_8px_#ef4444]' : 'bg-green-500 shadow-[0_0_8px_#22c55e]'}"></div>
      `,
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });
  };

  const createIncidentIcon = () => {
    return L.divIcon({
      className: 'custom-incident-icon',
      html: `
        <div class="relative flex items-center justify-center">
          <div class="absolute w-12 h-12 rounded-full bg-red-600/20 border-2 border-red-500 animate-ping opacity-70"></div>
          <div class="absolute w-8 h-8 rounded-full bg-red-600/40 border border-red-500 animate-ping opacity-90 delay-300"></div>
          <div class="w-6 h-6 rounded-full bg-red-600 border-2 border-white flex items-center justify-center shadow-[0_0_20px_#ef4444]">
            <span class="text-white text-[10px] font-black">⚠</span>
          </div>
        </div>
      `,
      iconSize: [48, 48],
      iconAnchor: [24, 24]
    });
  };

  return (
    <div className="w-full h-full relative rounded-xl overflow-hidden border border-gray-800 shadow-[0_8px_32px_rgba(0,0,0,0.5)] bg-[#0d0d0d]">
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={mapContainerStyle}
        zoomControl={true}
        key={`${mapCenter[0]}-${mapCenter[1]}-${mapZoom}`} // Re-render when center/zoom updates
      >
        {/* Dark Map Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Railway Line Polyline */}
        {trackPositions.length > 1 && (
          <Polyline
            positions={trackPositions}
            color="#222"
            weight={6}
            opacity={0.9}
          />
        )}
        {trackPositions.length > 1 && (
          <Polyline
            positions={trackPositions}
            color="#0ea5e9" // Glowing blue line inside
            weight={2}
            opacity={0.8}
            dashArray="8, 6"
          />
        )}

        {/* Station Markers */}
        {sortedStations.map((station) => (
          <Marker
            key={station.code}
            position={[station.lat, station.lng]}
            icon={createStationIcon(station.code)}
          >
            <Popup>
              <div className="text-gray-100 font-mono p-1">
                <h3 className="font-bold text-cyan-400 border-b border-gray-900 pb-1.5 mb-1.5">{station.name} ({station.code})</h3>
                <p className="text-xs text-gray-300 my-0.5"><strong>Division:</strong> <span className="text-gray-100">{station.division}</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Platforms:</strong> <span className="text-gray-100">{station.platforms}</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Station Master:</strong> <span className="text-gray-100">{station.station_master_contact}</span></p>
                <p className="text-xs text-gray-300 mt-1.5 pt-1 border-t border-gray-900 font-semibold font-mono">KM Marker: <span className="text-cyan-400">{station.km} km</span></p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Signal Block Section Markers */}
        {signalStates.map((sig) => (
          <Marker
            key={sig.signal_id}
            position={interpolateCoordsForKm(sig.km, stations)}
            icon={createSignalIcon(sig)}
          >
            <Popup>
              <div className="text-gray-100 font-mono text-xs">
                <p className="font-bold text-red-500 tracking-wide uppercase border-b border-gray-900 pb-1 mb-1">SIGNAL AUTOMATION LOCK</p>
                <p className="text-gray-300 my-0.5"><strong>ID:</strong> <span className="text-gray-100">{sig.signal_id}</span></p>
                <p className="text-gray-300 my-0.5"><strong>Location:</strong> <span className="text-gray-100">km {sig.km}</span></p>
                <p className="text-gray-300 my-0.5"><strong>Status:</strong> <span className="font-bold text-red-500">{sig.status}</span></p>
                <p className="italic mt-1.5 pt-1 border-t border-gray-900 text-[10px] text-gray-400">{sig.reason}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Incident Marker */}
        {activeIncident && activeIncident.location && (
          <Marker
            position={[activeIncident.location.lat, activeIncident.location.lng]}
            icon={createIncidentIcon()}
          >
            <Popup>
              <div className="text-gray-100 font-mono p-1">
                <h3 className="font-bold text-red-500 border-b border-red-950 pb-1.5 mb-1.5 uppercase tracking-wide">
                  ⚠ INCIDENT ZONE
                </h3>
                <p className="text-xs text-gray-300 my-0.5"><strong>ID:</strong> <span className="text-gray-100">{activeIncident.incident_id}</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Type:</strong> <span className="text-gray-100 uppercase">{activeIncident.type}</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Severity:</strong> <span className="text-gray-100">Level {activeIncident.severity}/3</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Track:</strong> <span className="text-gray-100">{activeIncident.track} Line</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Location:</strong> <span className="text-gray-100">km {activeIncident.location.km}</span></p>
                <p className="text-xs text-gray-300 my-0.5"><strong>Nearest Station:</strong> <span className="text-gray-100">{activeIncident.nearest_station}</span></p>
                <p className="text-xs font-bold text-red-500 mt-2 pt-1 border-t border-gray-900 uppercase">Status: RESPONSE ACTIVE</p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Train Markers */}
        {trains.map((train) => {
          if (!train.lat || !train.lng) return null;
          return (
            <Marker
              key={train.train_no}
              position={[train.lat, train.lng]}
              icon={createTrainIcon(train)}
            >
              <Popup>
                <div className="text-gray-100 font-mono p-1">
                  <h3 className="font-bold text-cyan-400 border-b border-gray-900 pb-1.5 mb-1.5">{train.name}</h3>
                  <p className="text-xs text-gray-300 my-0.5"><strong>Train No:</strong> <span className="text-gray-100">{train.train_no}</span></p>
                  <p className="text-xs text-gray-300 my-0.5"><strong>Direction:</strong> <span className="text-gray-100">{train.direction} (towards {train.direction === 'DOWN' ? 'Chennai' : 'Howrah'})</span></p>
                  <p className="text-xs text-gray-300 my-0.5"><strong>Speed:</strong> <span className={train.speed === 0 ? "text-red-500 font-bold" : "text-green-600 font-bold"}>{train.speed} km/h</span></p>
                  <p className="text-xs text-gray-300 my-0.5"><strong>Current Position:</strong> <span className="text-gray-100">km {Math.round(train.km)} (near {train.nearest_station})</span></p>
                  <p className="text-xs text-gray-300 mt-1.5 pt-1 border-t border-gray-900"><strong>Status:</strong> 
                    <span className={`ml-1 font-bold ${
                      train.status === 'RUNNING' ? 'text-green-600' :
                      train.status === 'HALTED' ? 'text-red-500' : 'text-yellow-600 animate-pulse'
                    }`}>{train.status}</span>
                  </p>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}

// Local helper to interpolate lat/lng based on a km marker for placing signals on the tracks
function interpolateCoordsForKm(km, stations) {
  if (stations.length === 0) return [18.5, 82.5];
  const sorted = [...stations].sort((a, b) => a.km - b.km);
  if (km <= sorted[0].km) return [sorted[0].lat, sorted[0].lng];
  if (km >= sorted[sorted.length - 1].km) return [sorted[sorted.length - 1].lat, sorted[sorted.length - 1].lng];

  for (let i = 0; i < sorted.length - 1; i++) {
    const s1 = sorted[i];
    const s2 = sorted[i+1];
    if (s1.km <= km && km <= s2.km) {
      const total = s2.km - s1.km;
      if (total === 0) return [s1.lat, s1.lng];
      const ratio = (km - s1.km) / total;
      return [
        s1.lat + ratio * (s2.lat - s1.lat),
        s1.lng + ratio * (s2.lng - s1.lng)
      ];
    }
  }
  return [sorted[0].lat, sorted[0].lng];
}
