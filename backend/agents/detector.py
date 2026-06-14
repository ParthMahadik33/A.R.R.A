from datetime import datetime
from backend.db.models import add_decision_log

class DetectorAgent:
    def __init__(self):
        self.name = "Detector Agent"

    def run(self, incident_data):
        """
        Classifies incident severity and determines affected block sections.
        """
        incident_id = incident_data["incident_id"]
        inc_type = incident_data["type"]
        severity = incident_data["severity"]
        km = incident_data["location"]["km"]
        track = incident_data["track"]
        
        # Determine human-readable severity description
        severity_mapping = {
            3: "CRITICAL (Immediate Collision Risk / Structural Failure)",
            2: "MAJOR (Track Blockage / Component Disruption)",
            1: "MINOR (Telemetry Anomaly / Precautionary State)"
        }
        severity_desc = severity_mapping.get(severity, "UNKNOWN")
        
        # Calculate affected track section bounds (typical block section is 2km before and after)
        affected_start = max(0, km - 2)
        affected_end = min(1661, km + 2)
        
        # Construct analysis summary
        summary = (
            f"Classified track circuit failure {incident_data['circuit_id']} near {incident_data['nearest_station']} "
            f"(km {km}) as {inc_type.upper()} with severity {severity_desc} on the {track} track."
        )
        
        result = {
            "incident_id": incident_id,
            "type": inc_type,
            "severity_value": severity,
            "severity_level": "CRITICAL" if severity == 3 else "WARNING" if severity == 2 else "INFO",
            "severity_description": severity_desc,
            "track_affected": track,
            "incident_km": km,
            "affected_zone": {
                "start_km": affected_start,
                "end_km": affected_end
            },
            "circuit_id": incident_data["circuit_id"],
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        }
        
        # Write to SQLite database audit logs
        add_decision_log(
            incident_id=incident_id,
            agent_name=self.name,
            step="CLASSIFY_INCIDENT",
            details=result,
            action_taken=f"Classified event as {inc_type.upper()} and mapped {affected_start}-{affected_end} km block section."
        )
        
        return result
