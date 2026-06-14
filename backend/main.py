import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Add root folder to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import HOST, PORT, DEBUG
from backend.db.models import init_db, create_incident, get_incident_logs
from backend.data.simulation import generate_incident, TrainSimulator
from backend.orchestrator import ArraOrchestrator

# Initialize Flask & SocketIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize DB on start
init_db()

# State
simulator = TrainSimulator()
orchestrator = ArraOrchestrator(simulator=simulator)
active_incident = None
background_thread = None
thread_lock = threading.Lock()

# Background task for continuous train updates
def train_update_loop():
    print("Background train update loop started.")
    while True:
        socketio.sleep(2.0)
        trains = simulator.update_positions()
        socketio.emit('trains_update', {'trains': trains})

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "ONLINE",
        "message": "ARRA (Autonomous Railway Response Architecture) Backend is running."
    })

@app.route('/api/status', methods=['GET'])
def get_status():

    return jsonify({
        "status": "ONLINE",
        "system": "ARRA (Autonomous Railway Response Architecture)",
        "groq_active": orchestrator.is_groq_active,
        "active_incident": active_incident
    })

@app.route('/api/stations', methods=['GET'])
def get_stations():
    from backend.data.simulation import STATIONS
    return jsonify(STATIONS)

@app.route('/api/depots', methods=['GET'])
def get_depots():
    from backend.data.simulation import DATA_DIR
    import json
    with open(os.path.join(DATA_DIR, 'art_depots.json'), 'r') as f:
        depots = json.load(f)
    return jsonify(depots)

@app.route('/api/logs/<incident_id>', methods=['GET'])
def get_logs(incident_id):
    logs = get_incident_logs(incident_id)
    return jsonify(logs)

# WebSocket connection
@socketio.on('connect')
def handle_connect():
    print("Frontend client connected.")
    # Send initial data immediately
    from backend.data.simulation import STATIONS
    emit('init_data', {
        'stations': STATIONS,
        'trains': simulator.get_all_trains(),
        'groq_active': orchestrator.is_groq_active
    })

# Trigger Incident WebSocket Event
@socketio.on('trigger_incident')
def handle_trigger_incident(data):
    global active_incident
    print(f"Trigger incident request received: {data}")
    
    # Generate custom or random incident
    incident_type = data.get('type')
    station_code = data.get('station')
    severity = data.get('severity')
    demo_mode = data.get('demo_mode', False)
    
    incident = generate_incident(
        incident_type=incident_type, 
        target_station=station_code, 
        severity=severity
    )
    active_incident = incident
    
    # Save to SQLite
    create_incident(incident)
    
    # Broadcast incident trigger to frontend to spawn overlay & alert sounds
    socketio.emit('incident_triggered', incident)
    
    # Run Orchestrator in a background thread to prevent blocking WebSocket server
    def run_pipeline():
        def socket_emit(event, payload):
            socketio.emit(event, payload)
            
        if demo_mode:
            print(f"Demo mode active. Repositioning train relative to km {incident['location']['km']}")
            repositioned = simulator.prepare_demo_positions(incident['location']['km'], incident['track'])
            print(f"Repositioned train for demo mode: {repositioned}")
            # Immediately update the map with new coordinates
            socketio.emit('trains_update', {'trains': simulator.get_all_trains()})
            time.sleep(0.1)  # 100ms delay to let the frontend update
            
        orchestrator.run(incident, socket_emit)
        
    socketio.start_background_task(run_pipeline)

# Reset Simulation
@socketio.on('reset_simulation')
def handle_reset_simulation():
    global active_incident
    print("Resetting simulator state...")
    simulator.reset_trains()
    active_incident = None
    socketio.emit('simulation_reset', {
        'trains': simulator.get_all_trains()
    })

if __name__ == '__main__':
    # Start background loop
    socketio.start_background_task(train_update_loop)
    
    print(f"Starting ARRA Backend Server on http://{HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
