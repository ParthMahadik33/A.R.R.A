from datetime import datetime
from backend.db.models import add_decision_log
from backend.config import COLLISION_CRITICAL_MIN, COLLISION_WARNING_MIN

class CollisionCalculatorAgent:
    def __init__(self):
        self.name = "Collision Calculator Agent"

    def run(self, incident_data, active_trains):
        """
        Calculates collision risk for all trains near the incident site.
        """
        incident_id = incident_data["incident_id"]
        inc_km = incident_data["location"]["km"]
        inc_track = incident_data["track"]
        inc_type = incident_data["type"]
        severity = incident_data["severity"]
        
        trains_at_risk = []
        
        for train in active_trains:
            # Determine if train is on a track that could be affected.
            # If derailment (severity >= 2), both tracks are at risk.
            is_track_risk = False
            if inc_type == 'derailment' or severity == 3:
                is_track_risk = True  # Double track hazard (Balasore case)
            else:
                is_track_risk = (train["direction"] == inc_track)
                
            if not is_track_risk:
                continue
                
            # Calculate distance and direction of approach
            distance = 0.0
            is_approaching = False
            
            if train["direction"] == "DOWN":
                # Moving Howrah (0) -> Chennai (1661). Approaching if train is behind the incident km.
                if train["km"] < inc_km:
                    distance = inc_km - train["km"]
                    is_approaching = True
            else: # UP
                # Moving Chennai (1661) -> Howrah (0). Approaching if train is ahead of the incident km.
                if train["km"] > inc_km:
                    distance = train["km"] - inc_km
                    is_approaching = True
                    
            if not is_approaching:
                continue
                
            # Calculate Time-to-Collision (TTC) in minutes
            speed = train["speed"]
            if speed > 0:
                ttc_minutes = (distance / speed) * 60.0
            else:
                ttc_minutes = float('inf')  # Already stationary
                
            # Classify urgency
            if ttc_minutes <= COLLISION_CRITICAL_MIN:
                urgency = "CRITICAL"
            elif ttc_minutes <= COLLISION_WARNING_MIN:
                urgency = "WARNING"
            elif ttc_minutes <= 15.0:
                urgency = "MONITOR"
            else:
                urgency = "SAFE"
                
            trains_at_risk.append({
                "train_no": train["train_no"],
                "name": train["name"],
                "direction": train["direction"],
                "speed_kmh": speed,
                "current_km": round(train["km"], 2),
                "distance_km": round(distance, 2),
                "time_to_collision_mins": round(ttc_minutes, 2) if speed > 0 else "HALTED",
                "urgency": urgency,
                "nearest_station": train.get("nearest_station", "Unknown")
            })
            
        # Sort by proximity/time-to-collision
        trains_at_risk.sort(key=lambda x: (
            0 if x["urgency"] == "CRITICAL" else 
            1 if x["urgency"] == "WARNING" else 
            2 if x["urgency"] == "MONITOR" else 3,
            x["distance_km"]
        ))
        
        # Format summary
        critical_count = sum(1 for t in trains_at_risk if t["urgency"] == "CRITICAL")
        warning_count = sum(1 for t in trains_at_risk if t["urgency"] == "WARNING")
        
        summary = (
            f"Evaluated risk for {len(active_trains)} corridor trains. "
            f"Found {len(trains_at_risk)} approaching trains. "
            f"CRITICAL: {critical_count}, WARNING: {warning_count}."
        )
        
        result = {
            "incident_id": incident_id,
            "trains_at_risk": trains_at_risk,
            "critical_risk_count": critical_count,
            "warning_risk_count": warning_count,
            "summary": summary
        }
        
        add_decision_log(
            incident_id=incident_id,
            agent_name=self.name,
            step="CALCULATE_COLLISION_RISK",
            details=result,
            action_taken=f"Identified {critical_count} critical and {warning_count} warning train risks."
        )
        
        return result
