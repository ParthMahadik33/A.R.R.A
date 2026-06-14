import random
import time
import json
import os
from datetime import datetime
from backend.config import DATA_DIR

# Load stations data
STATIONS_PATH = os.path.join(DATA_DIR, 'stations.json')
with open(STATIONS_PATH, 'r') as f:
    STATIONS = json.load(f)

# Sort stations by kilometer marker
STATIONS_SORTED = sorted(STATIONS, key=lambda s: s['km'])

def get_station_by_code(code):
    for s in STATIONS:
        if s['code'] == code:
            return s
    return None

def find_nearest_station(km):
    nearest = STATIONS_SORTED[0]
    min_diff = abs(km - nearest['km'])
    
    for s in STATIONS_SORTED[1:]:
        diff = abs(km - s['km'])
        if diff < min_diff:
            min_diff = diff
            nearest = s
    return nearest

def interpolate_coordinates(km):
    """Interpolate coordinates for a train at a given kilometer marker."""
    if km <= STATIONS_SORTED[0]['km']:
        return STATIONS_SORTED[0]['lat'], STATIONS_SORTED[0]['lng']
    if km >= STATIONS_SORTED[-1]['km']:
        return STATIONS_SORTED[-1]['lat'], STATIONS_SORTED[-1]['lng']
        
    for i in range(len(STATIONS_SORTED) - 1):
        s1 = STATIONS_SORTED[i]
        s2 = STATIONS_SORTED[i+1]
        if s1['km'] <= km <= s2['km']:
            # Linear interpolation
            total_dist = s2['km'] - s1['km']
            if total_dist == 0:
                return s1['lat'], s1['lng']
            ratio = (km - s1['km']) / total_dist
            lat = s1['lat'] + ratio * (s2['lat'] - s1['lat'])
            lng = s1['lng'] + ratio * (s2['lng'] - s1['lng'])
            return round(lat, 6), round(lng, 6)
            
    return STATIONS_SORTED[0]['lat'], STATIONS_SORTED[0]['lng']

def generate_incident(incident_type=None, target_station=None, severity=None):
    """Generate a realistic incident event."""
    types = ['derailment', 'obstruction', 'signal_failure']
    inc_type = incident_type if incident_type in types else random.choice(types)
    
    # Choose station, default to Balasore (iconic for Indian Railways context)
    station = None
    if target_station:
        station = get_station_by_code(target_station) or find_nearest_station(147)
    else:
        # Balasore (BLS) or Cuttack (CTC) or Rajahmundry (RJY)
        demo_stations = ['BLS', 'CTC', 'RJY', 'PSA', 'BHC']
        station = get_station_by_code(random.choice(demo_stations))
        
    severity_val = severity if severity in [1, 2, 3] else random.randint(2, 3)
    track = random.choice(['UP', 'DOWN'])
    
    # Calculate a random km marker near the station (within 5-15 km)
    offset = random.randint(-15, 15)
    if offset == 0:
        offset = 5
    km = max(10, min(1650, station['km'] + offset))
    
    # Find closest station to this actual km
    actual_nearest = find_nearest_station(km)
    lat, lng = interpolate_coordinates(km)
    
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
    circuit_id = f"{actual_nearest['code']}-TC-{random.randint(10, 99)}"
    
    return {
        "incident_id": incident_id,
        "timestamp": datetime.now().isoformat(),
        "type": inc_type,
        "severity": severity_val,
        "track": track,
        "location": {
            "km": km,
            "lat": lat,
            "lng": lng
        },
        "nearest_station": actual_nearest['name'],
        "nearest_station_code": actual_nearest['code'],
        "circuit_id": circuit_id
    }

class TrainSimulator:
    def __init__(self):
        # Define 8 major trains running along the Howrah-Chennai corridor
        self.trains = [
            {
                "train_no": "12841",
                "name": "Coromandel Express",
                "direction": "DOWN",  # Howrah (km 0) -> Chennai (km 1661)
                "km": 120.0,          # Starting at km 120 (near Kharagpur heading to Balasore)
                "speed": 110,
                "target_speed": 110,
                "status": "RUNNING"
            },
            {
                "train_no": "12842",
                "name": "Coromandel Express (Return)",
                "direction": "UP",    # Chennai -> Howrah
                "km": 300.0,          # Near Bhadrak heading to Balasore/Kharagpur
                "speed": 105,
                "target_speed": 105,
                "status": "RUNNING"
            },
            {
                "train_no": "12863",
                "name": "Howrah - Bengaluru SF Express",
                "direction": "DOWN",
                "km": 420.0,          # Near Bhubaneswar heading south
                "speed": 95,
                "target_speed": 95,
                "status": "RUNNING"
            },
            {
                "train_no": "12864",
                "name": "Bengaluru - Howrah SF Express",
                "direction": "UP",
                "km": 500.0,          # Near Balugaon heading north
                "speed": 90,
                "target_speed": 90,
                "status": "RUNNING"
            },
            {
                "train_no": "12703",
                "name": "Falaknuma Express",
                "direction": "DOWN",
                "km": 1120.0,         # Near Rajahmundry heading south
                "speed": 100,
                "target_speed": 100,
                "status": "RUNNING"
            },
            {
                "train_no": "12704",
                "name": "Falaknuma Express (Return)",
                "direction": "UP",
                "km": 1280.0,         # Near Vijayawada heading north
                "speed": 105,
                "target_speed": 105,
                "status": "RUNNING"
            },
            {
                "train_no": "12245",
                "name": "Howrah - Yesvantpur Duronto",
                "direction": "DOWN",
                "km": 800.0,          # Near Srikakulam Road heading south
                "speed": 110,
                "target_speed": 110,
                "status": "RUNNING"
            },
            {
                "train_no": "12246",
                "name": "Yesvantpur - Howrah Duronto",
                "direction": "UP",
                "km": 980.0,          # Near Duvvada heading north
                "speed": 110,
                "target_speed": 110,
                "status": "RUNNING"
            }
        ]
        self.last_update_time = time.time()
        self._initialize_coordinates()
        
    def _initialize_coordinates(self):
        for train in self.trains:
            lat, lng = interpolate_coordinates(train['km'])
            train['lat'] = lat
            train['lng'] = lng
            train['last_updated'] = datetime.now().isoformat()

    def update_positions(self):
        """Update train positions based on elapsed time and target speeds."""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Convert dt from seconds to hours for speed calculation (speed is in km/h)
        dt_hours = dt / 3600.0
        
        # Accelerate or decelerate trains to match target_speed
        for train in self.trains:
            # Simple inertia simulation
            if train['speed'] < train['target_speed']:
                train['speed'] = min(train['target_speed'], train['speed'] + 10 * dt)
            elif train['speed'] > train['target_speed']:
                # Emergency brake decelerates faster
                decel_rate = 25 if train['target_speed'] == 0 else 10
                train['speed'] = max(train['target_speed'], train['speed'] - decel_rate * dt)
                
            # Update km marker
            # DOWN trains: km increases (towards Chennai Central at km 1661)
            # UP trains: km decreases (towards Howrah at km 0)
            distance_travelled = train['speed'] * dt_hours
            
            if train['direction'] == 'DOWN':
                train['km'] = min(1661.0, train['km'] + distance_travelled)
                # Wrap around for loop simulation if they reach the end
                if train['km'] >= 1661.0:
                    train['km'] = 0.0
            else:
                train['km'] = max(0.0, train['km'] - distance_travelled)
                if train['km'] <= 0.0:
                    train['km'] = 1661.0
                    
            # Update coordinates
            lat, lng = interpolate_coordinates(train['km'])
            train['lat'] = lat
            train['lng'] = lng
            train['last_updated'] = datetime.now().isoformat()
            
            # Update status string
            if train['speed'] == 0:
                train['status'] = "HALTED"
            elif train['speed'] < train['target_speed'] * 0.6:
                train['status'] = "CAUTION"
            else:
                train['status'] = "RUNNING"
                
        return self.get_all_trains()

    def apply_emergency_braking(self, train_no):
        for train in self.trains:
            if train['train_no'] == train_no:
                train['target_speed'] = 0
                train['status'] = "HALTING"
                return True
        return False
        
    def reset_trains(self):
        """Reset all trains to running status and original positions."""
        self.__init__()

    def prepare_demo_positions(self, incident_km, incident_track):
        """Reposition closest approaching train to be exactly 5km (2.7 min) away."""
        # Idempotency check: see if a train is already at the target demo position
        for t in self.trains:
            expected_km = incident_km - 5.0 if t["direction"] == "DOWN" else incident_km + 5.0
            if abs(t["km"] - expected_km) < 0.01:
                return {
                    "train_no": t["train_no"],
                    "name": t["name"]
                }

        # 1. Find approaching trains
        approaching_trains = []
        for t in self.trains:
            is_approaching = False
            if t["direction"] == "DOWN" and t["km"] < incident_km:
                is_approaching = True
            elif t["direction"] == "UP" and t["km"] > incident_km:
                is_approaching = True
                
            if is_approaching:
                dist = abs(t["km"] - incident_km)
                approaching_trains.append((t, dist))
                
        if approaching_trains:
            # Sort by distance to find the closest
            approaching_trains.sort(key=lambda x: x[1])
            target_train = approaching_trains[0][0]
        else:
            # Fallback to the first DOWN train
            down_trains = [t for t in self.trains if t["direction"] == "DOWN"]
            target_train = down_trains[0] if down_trains else self.trains[0]

        # 2. Position exactly 5km away (max/min to keep it within track range)
        target_km = incident_km - 5.0 if target_train["direction"] == "DOWN" else incident_km + 5.0

        target_km = max(0.0, min(1661.0, target_km))
        
        target_train["km"] = target_km
        
        # Interpolate coordinates
        lat, lng = interpolate_coordinates(target_train["km"])
        target_train["lat"] = lat
        target_train["lng"] = lng
        
        # Reset speeds to running state
        original_speed = 110 if "Coromandel" in target_train["name"] else 105
        target_train["speed"] = original_speed
        target_train["target_speed"] = original_speed
        target_train["status"] = "RUNNING"
        target_train["last_updated"] = datetime.now().isoformat()
        
        return {
            "train_no": target_train["train_no"],
            "name": target_train["name"]
        }

    def get_all_trains(self):
        # Add nearest station context to each train
        res = []
        for t in self.trains:
            s = find_nearest_station(t['km'])
            train_copy = t.copy()
            train_copy['nearest_station'] = s['name']
            train_copy['nearest_station_code'] = s['code']
            res.append(train_copy)
        return res
