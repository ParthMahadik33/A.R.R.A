import os
from datetime import datetime
from backend.db.models import add_decision_log

class CommunicationsAgent:
    def __init__(self):
        self.name = "Communications Agent"

    def run(self, incident_data, collision_data, rescue_data, gemini_helper=None):
        """
        Generates multilingual alerts, DRM broadcasts, and public statements.
        """
        incident_id = incident_data["incident_id"]
        inc_type = incident_data["type"]
        severity = incident_data["severity"]
        km = incident_data["location"]["km"]
        station = incident_data["nearest_station"]
        track = incident_data["track"]
        
        trains_at_risk = collision_data.get("trains_at_risk", [])
        stopped_trains_str = ", ".join([f"{t['train_no']} ({t['name']})" for t in trains_at_risk if t["urgency"] in ["CRITICAL", "WARNING"]])
        if not stopped_trains_str:
            stopped_trains_str = "None within critical range"
            
        depot_name = rescue_data["dispatch_order"]["depot_name"]
        art_eta = rescue_data["dispatch_order"]["eta_minutes"]
        hospital_name = rescue_data["hospital_alert"]["hospital_name"]
        
        # 1. DRM Alert Format
        drm_alert = (
            f"URGENT — ARRA SYSTEM INCIDENT ALERT\n"
            f"-----------------------------------------\n"
            f"Incident ID: {incident_id}\n"
            f"Alert Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST\n"
            f"Location: km {km}, Howrah-Chennai Main Line, near {station}\n"
            f"Incident Type: {inc_type.upper()} | Severity: {severity}/3\n"
            f"Track Affected: {track} Track\n"
            f"Approaching Trains Halted: {stopped_trains_str}\n"
            f"Accident Relief Train: Dispatched from {depot_name} (ETA: {art_eta} min)\n"
            f"Medical Mobilization: Alert sent to {hospital_name}\n"
            f"Action Required: Command Center verify and transition to recovery state."
        )
        
        # 2. Hindi & English Station announcements
        # Default templates
        primary_train = trains_at_risk[0] if trains_at_risk else {"train_no": "Approaching Trains", "name": ""}
        train_no = primary_train["train_no"]
        train_name = primary_train["name"]
        
        pa_english = (
            f"Attention passengers. Train number {train_no} {train_name} is being halted near {station} "
            f"due to an automated track safety protocol. Please remain calm, stay inside your coaches, "
            f"and follow instructions from the train staff. The Railway Emergency Force is actively managing the situation. "
            f"Inconvenience is regretted."
        )
        
        pa_hindi = (
            f"यात्रियों का ध्यान दें। ट्रेन संख्या {train_no} {train_name} को ट्रैक सुरक्षा प्रोटोकॉल के कारण "
            f"{station} के पास रोका जा रहा है। कृपया शांत रहें, अपने कोच के अंदर बने रहें, "
            f"और ट्रेन कर्मचारियों के निर्देशों का पालन करें। रेलवे आपातकालीन बल सक्रिय रूप से स्थिति का प्रबंधन कर रहा है। "
            f"असुविधा के लिए खेद है।"
        )
        
        # 3. Public Press Release
        press_release = (
            f"PRESS RELEASE — MINISTRY OF RAILWAYS (EAST COAST DIVISION)\n"
            f"Date: {datetime.now().strftime('%d %B %Y')}\n\n"
            f"At approximately {datetime.now().strftime('%H:%M')} hours today, the Autonomous Railway Response Architecture (ARRA) "
            f"detected a track circuit discontinuity ({incident_data['circuit_id']}) at km {km} near {station} station on the {track} track, "
            f"classified as a {inc_type}.\n\n"
            f"ARRA immediately initiated safety protocols: emergency stop signals were transmitted to all approaching trains, "
            f"halting traffic. An Accident Relief Train (ART) has been mobilized from {depot_name} and is enroute (ETA {art_eta} minutes). "
            f"Local medical facilities, including {hospital_name}, have been placed on high alert and emergency response vehicles are dispatching to the coordinates.\n\n"
            f"Due to autonomous signaling intervention, a potential collision scenario was averted. Further updates on track restoration will be released shortly."
        )
        
        # If Gemini helper is available, we can use it to polish these announcements!
        if gemini_helper:
            try:
                polished = gemini_helper.polish_communications(inc_type, severity, station, km, stopped_trains_str, depot_name, art_eta)
                if polished:
                    drm_alert = polished.get("drm_alert", drm_alert)
                    pa_english = polished.get("pa_english", pa_english)
                    pa_hindi = polished.get("pa_hindi", pa_hindi)
                    press_release = polished.get("press_release", press_release)
            except Exception as e:
                # Log error and fallback silently
                print(f"Communications Agent LLM Polish Error: {e}")
                
        result = {
            "incident_id": incident_id,
            "drm_alert": drm_alert,
            "announcements": {
                "english": pa_english,
                "hindi": pa_hindi
            },
            "public_statement": press_release,
            "timestamp": datetime.now().isoformat()
        }
        
        add_decision_log(
            incident_id=incident_id,
            agent_name=self.name,
            step="GENERATE_COMMUNICATIONS",
            details=result,
            action_taken=f"Generated DRM alerts, press statement, and bilingual PA announcements."
        )
        
        return result
