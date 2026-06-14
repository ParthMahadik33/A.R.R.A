from datetime import datetime
from backend.db.models import add_decision_log

class SignalControllerAgent:
    def __init__(self):
        self.name = "Signal Controller Agent"

    def run(self, incident_data, collision_data):
        """
        Determines and issues signal state flips (to RED) and emergency braking commands.
        """
        incident_id = incident_data["incident_id"]
        inc_km = incident_data["location"]["km"]
        nearest_station = incident_data["nearest_station_code"]
        trains_at_risk = collision_data.get("trains_at_risk", [])
        
        signal_commands = []
        train_commands = []
        
        # 1. Flip signals in the immediate block section to RED.
        # Typically, we have signals at every 2 km block interval.
        # We lock signals covering the affected range (e.g. 5km before and after the incident)
        affected_range_start = max(0, inc_km - 5)
        affected_range_end = min(1661, inc_km + 5)
        
        # Generate block signal codes to flip
        for km_marker in range(int(affected_range_start), int(affected_range_end) + 1, 2):
            sig_id = f"SIG-{nearest_station}-{km_marker}"
            signal_commands.append({
                "signal_id": sig_id,
                "km": km_marker,
                "status": "STOP",
                "color": "RED",
                "reason": "Incident affected block section"
            })
            
        # 2. Issue halting commands to any train with Critical or Warning status
        for train in trains_at_risk:
            if train["urgency"] in ["CRITICAL", "WARNING"]:
                train_commands.append({
                    "train_no": train["train_no"],
                    "name": train["name"],
                    "command": "EMERGENCY_BRAKE",
                    "reason": f"Train is approaching {incident_data['type']} on {train['direction']} track (TTC: {train['time_to_collision_mins']} mins)",
                    "distance_km": train["distance_km"]
                })
                
        summary = (
            f"Issued STOP command to {len(signal_commands)} block signals in range {affected_range_start}-{affected_range_end} km. "
            f"Sent EMERGENCY_BRAKE commands to {len(train_commands)} high-risk trains."
        )
        
        result = {
            "incident_id": incident_id,
            "signal_commands": signal_commands,
            "train_commands": train_commands,
            "affected_range": {
                "start": affected_range_start,
                "end": affected_range_end
            },
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        add_decision_log(
            incident_id=incident_id,
            agent_name=self.name,
            step="CONTROL_SIGNALS",
            details=result,
            action_taken=f"Set {len(signal_commands)} signals to RED. Commanded emergency braking for trains: {', '.join([t['train_no'] for t in train_commands])}."
        )
        
        return result
