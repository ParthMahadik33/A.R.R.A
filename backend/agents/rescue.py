import os
import json
import math
from datetime import datetime
from backend.db.models import add_decision_log
from backend.config import DATA_DIR

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points in km."""
    R = 6371.0  # Earth's radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

class RescueCoordinatorAgent:
    def __init__(self):
        self.name = "Rescue Coordinator Agent"
        # Load ART depots data
        depots_path = os.path.join(DATA_DIR, 'art_depots.json')
        with open(depots_path, 'r') as f:
            self.depots = json.load(f)

    def run(self, incident_data):
        """
        Identifies nearest ART depot and local hospitals, calculating ETAs and generating dispatch orders.
        """
        incident_id = incident_data["incident_id"]
        inc_lat = incident_data["location"]["lat"]
        inc_lng = incident_data["location"]["lng"]
        inc_km = incident_data["location"]["km"]
        
        # 1. Find the nearest ART Depot
        nearest_depot = None
        min_depot_dist = float('inf')
        
        for depot in self.depots:
            dist = haversine(depot["lat"], depot["lng"], inc_lat, inc_lng)
            if dist < min_depot_dist:
                min_depot_dist = dist
                nearest_depot = depot
                
        # Calculate ART Dispatch ETA (average speed 60 km/h, plus 15 mins turnout/mobilization time)
        art_speed = 60.0 # km/h
        travel_time_mins = (min_depot_dist / art_speed) * 60.0
        mobilization_time_mins = 15.0
        art_eta_mins = int(travel_time_mins + mobilization_time_mins)
        
        # 2. Find the nearest Hospital
        nearest_hospital = None
        min_hosp_dist = float('inf')
        
        # In our database, hospitals are nested inside depots, or we can check hospitals of all depots.
        for depot in self.depots:
            for hosp in depot["hospitals"]:
                dist = haversine(hosp["lat"], hosp["lng"], inc_lat, inc_lng)
                if dist < min_hosp_dist:
                    min_hosp_dist = dist
                    nearest_hospital = hosp
                    
        # Calculate Hospital Ambulance ETA (speed 50 km/h, plus 5 mins dispatch time)
        hosp_speed = 50.0 # km/h
        hosp_eta_mins = int((min_hosp_dist / hosp_speed) * 60.0 + 5.0)
        
        # Generate rescue commands and manifests
        dispatch_order = {
            "depot_id": nearest_depot["id"],
            "depot_name": nearest_depot["name"],
            "distance_km": round(min_depot_dist, 2),
            "eta_minutes": art_eta_mins,
            "equipment_dispatched": nearest_depot["equipment"],
            "command": "DISPATCH_IMMEDIATE_ART",
            "timestamp": datetime.now().isoformat()
        }
        
        hospital_alert = {
            "hospital_name": nearest_hospital["name"],
            "distance_km": round(min_hosp_dist, 2),
            "eta_minutes": hosp_eta_mins,
            "beds_available": nearest_hospital["beds_available"],
            "contact": nearest_hospital["contact"],
            "command": "MOBILIZE_TRAUMA_UNITS_AND_AMBULANCES",
            "message": (
                f"ALERT: Railway incident near km {inc_km} ({incident_data['nearest_station']}). "
                f"Severe {incident_data['type']}. Mobilize emergency ward and dispatch ambulances immediately."
            ),
            "timestamp": datetime.now().isoformat()
        }
        
        summary = (
            f"Nearest ART Depot: {nearest_depot['name']} (Dist: {round(min_depot_dist, 1)}km, ETA: {art_eta_mins}m). "
            f"Alerted Hospital: {nearest_hospital['name']} (Dist: {round(min_hosp_dist, 1)}km, ETA: {hosp_eta_mins}m, Available Beds: {nearest_hospital['beds_available']})."
        )
        
        result = {
            "incident_id": incident_id,
            "dispatch_order": dispatch_order,
            "hospital_alert": hospital_alert,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        add_decision_log(
            incident_id=incident_id,
            agent_name=self.name,
            step="COORDINATE_RESCUE",
            details=result,
            action_taken=f"Dispatched ART from {nearest_depot['station_code']} (ETA: {art_eta_mins} min) and alerted {nearest_hospital['name']}."
        )
        
        return result
