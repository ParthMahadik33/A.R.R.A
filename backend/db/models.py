import sqlite3
import os
import json
from datetime import datetime
from backend.config import DB_PATH, DB_DIR

def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Incidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            severity INTEGER NOT NULL,
            track TEXT NOT NULL,
            km INTEGER NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            nearest_station TEXT NOT NULL,
            circuit_id TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    
    # Decision/Audit Log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            step TEXT NOT NULL,
            details TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_incident(incident):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO incidents (incident_id, timestamp, type, severity, track, km, lat, lng, nearest_station, circuit_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident['incident_id'],
            incident['timestamp'],
            incident['type'],
            incident['severity'],
            incident['track'],
            incident['location']['km'],
            incident['location']['lat'],
            incident['location']['lng'],
            incident['nearest_station'],
            incident['circuit_id'],
            'ACTIVE'
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # If already exists, we overwrite or ignore
        pass
    finally:
        conn.close()

def add_decision_log(incident_id, agent_name, step, details, action_taken, status='SUCCESS'):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    # Serialize details if it's a dict
    if isinstance(details, (dict, list)):
        details_str = json.dumps(details)
    else:
        details_str = str(details)
        
    cursor.execute('''
        INSERT INTO decision_logs (incident_id, agent_name, timestamp, step, details, action_taken, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (incident_id, agent_name, timestamp, step, details_str, action_taken, status))
    conn.commit()
    conn.close()

def get_incident_logs(incident_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM decision_logs 
        WHERE incident_id = ? 
        ORDER BY timestamp ASC
    ''', (incident_id,))
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for r in rows:
        try:
            details_parsed = json.loads(r['details'])
        except Exception:
            details_parsed = r['details']
            
        logs.append({
            "id": r["id"],
            "incident_id": r["incident_id"],
            "agent_name": r["agent_name"],
            "timestamp": r["timestamp"],
            "step": r["step"],
            "details": details_parsed,
            "action_taken": r["action_taken"],
            "status": r["status"]
        })
    return logs
