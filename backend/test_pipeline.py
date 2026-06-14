import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.models import init_db, get_incident_logs, create_incident
from backend.data.simulation import generate_incident, TrainSimulator
from backend.agents.detector import DetectorAgent
from backend.agents.collision import CollisionCalculatorAgent
from backend.agents.signal import SignalControllerAgent
from backend.agents.rescue import RescueCoordinatorAgent
from backend.agents.communications import CommunicationsAgent

def run_test():
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
    print("=== ARRA PIPELINE DIAGNOSTIC TEST ===")
    
    # 1. Initialize DB
    print("\n[Step 1] Initializing SQLite database...")
    init_db()
    print("Database initialized successfully.")
    
    # 2. Generate Incident
    print("\n[Step 2] Injecting track circuit disruption near Balasore...")
    incident = generate_incident(incident_type='derailment', target_station='BLS', severity=3)
    print(f"Generated Incident: {json.dumps(incident, indent=2)}")
    create_incident(incident)
    
    # 3. Instantiate Agents & Simulator
    print("\n[Step 3] Loading telemetry assets and safety agents...")
    simulator = TrainSimulator()
    detector = DetectorAgent()
    collision = CollisionCalculatorAgent()
    signal = SignalControllerAgent()
    rescue = RescueCoordinatorAgent()
    comm = CommunicationsAgent()
    
    active_trains = simulator.get_all_trains()
    print(f"Loaded {len(active_trains)} active trains along Howrah-Chennai corridor.")
    
    # 4. Run Detector Agent
    print("\n[Step 4] Triggering Detector Agent...")
    det_out = detector.run(incident)
    print(f"Detector Summary: {det_out['summary']}")
    
    # 5. Run Collision Agent
    print("\n[Step 5] Triggering Collision Calculator Agent...")
    col_out = collision.run(incident, active_trains)
    print(f"Collision Summary: {col_out['summary']}")
    for t in col_out["trains_at_risk"]:
        print(f"  * Train {t['train_no']} ({t['name']}): Dist {t['distance_km']}km, TTC {t['time_to_collision_mins']} min [{t['urgency']}]")
        
    # 6. Run Signal Agent
    print("\n[Step 6] Triggering Signal Controller Agent...")
    sig_out = signal.run(incident, col_out)
    print(f"Signal Summary: {sig_out['summary']}")
    print(f"  * Signals set to RED: {len(sig_out['signal_commands'])}")
    print(f"  * Emergency brakes transmitted: {len(sig_out['train_commands'])}")
    
    # 7. Run Rescue Agent
    print("\n[Step 7] Triggering Rescue Coordinator Agent...")
    res_out = rescue.run(incident)
    print(f"Rescue Summary: {res_out['summary']}")
    print(f"  * Dispatch Order: {res_out['dispatch_order']['command']} (ART: {res_out['dispatch_order']['depot_name']}, ETA: {res_out['dispatch_order']['eta_minutes']} min)")
    print(f"  * Hospital Alert: {res_out['hospital_alert']['command']} (Hospital: {res_out['hospital_alert']['hospital_name']}, Beds: {res_out['hospital_alert']['beds_available']})")
    
    # 8. Run Communications Agent
    print("\n[Step 8] Triggering Communications Agent...")
    comm_out = comm.run(incident, col_out, res_out)
    print(f"Communications Summary: PA Scripts and DRM Bulletins generated.")
    print("------------------------------------------")
    print("PA ENGLISH BROADCAST SCRIPT:")
    print(f"\"{comm_out['announcements']['english']}\"")
    print("------------------------------------------")
    print("PA HINDI BROADCAST SCRIPT:")
    print(f"\"{comm_out['announcements']['hindi']}\"")
    print("------------------------------------------")
    
    # 9. Verify SQLite Logs
    print("\n[Step 9] Auditing SQLite incident logs database...")
    logs = get_incident_logs(incident["incident_id"])
    print(f"Retrieved {len(logs)} audit entries for incident ID: {incident['incident_id']}")
    for index, log in enumerate(logs):
        print(f"  {index + 1}. [{log['agent_name']}] -> {log['step']}: {log['action_taken']}")
        
    print("\n=== ARRA PIPELINE DIAGNOSTIC COMPLETED WITH 0 ERRORS ===")

if __name__ == '__main__':
    run_test()
