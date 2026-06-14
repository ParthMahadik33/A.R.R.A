import time
import json
from datetime import datetime
import requests
from backend.config import GROQ_API_KEY
from backend.agents.detector import DetectorAgent
from backend.agents.collision import CollisionCalculatorAgent
from backend.agents.signal import SignalControllerAgent
from backend.agents.rescue import RescueCoordinatorAgent
from backend.agents.communications import CommunicationsAgent
from backend.db.models import add_decision_log

class ArraOrchestrator:
    def __init__(self, simulator=None):
        self.simulator = simulator
        
        # Instantiate python agents
        self.detector = DetectorAgent()
        self.collision_calculator = CollisionCalculatorAgent()
        self.signal_controller = SignalControllerAgent()
        self.rescue_coordinator = RescueCoordinatorAgent()
        self.communications = CommunicationsAgent()
        
        # Keep track of running states
        self.is_groq_active = len(GROQ_API_KEY.strip()) > 0

    def run(self, incident_data, emit_fn):
        """
        Runs the full response pipeline.
        incident_data: The triggered incident event.
        emit_fn: WebSocket emit function to send real-time logs and statuses.
        """
        incident_id = incident_data["incident_id"]
        emit_fn("orchestrator_log", {"text": "ARRA Response Core v1.0.0 Online.\n", "type": "info"})
        time.sleep(0.5)
        
        emit_fn("orchestrator_log", {"text": f"Telemetry Input: Track discontinuity on {incident_data['circuit_id']} at km {incident_data['location']['km']}.\n", "type": "telemetry"})
        time.sleep(0.5)

        if self.is_groq_active:
            emit_fn("orchestrator_log", {"text": "Initializing Groq Llama 3.3 70B agentic reasoning...\n", "type": "system"})
            try:
                self._run_with_groq(incident_data, emit_fn)
            except Exception as e:
                emit_fn("orchestrator_log", {"text": f"Groq loop failed: {str(e)}. Running deterministic rules...\n", "type": "warning"})
                self._run_deterministic(incident_data, emit_fn)
        else:
            emit_fn("orchestrator_log", {"text": "No Groq API key available. Running deterministic rules...\n", "type": "system"})
            self._run_deterministic(incident_data, emit_fn)

    def _run_deterministic(self, incident_data, emit_fn):
        """Runs the agents in order, streaming thoughts and outcomes with delays."""
        incident_id = incident_data["incident_id"]
        
        # 1. Detector Agent
        emit_fn("orchestrator_log", {"text": "THOUGHT: Analyzing circuit telemetry data to classify the incident...\n", "type": "thought"})
        emit_fn("agent_status", {"agent": "detector", "status": "running"})
        time.sleep(1.2)
        
        detector_res = self.detector.run(incident_data)
        emit_fn("agent_status", {"agent": "detector", "status": "success", "summary": detector_res["summary"]})
        emit_fn("orchestrator_log", {"text": f"[Detector Agent Output] Type: {detector_res['type'].upper()} | Severity: {detector_res['severity_level']} | Sector bounds: km {detector_res['affected_zone']['start_km']}-{detector_res['affected_zone']['end_km']}\n", "type": "agent"})
        time.sleep(1.0)
        
        # 2. Collision Calculator Agent
        emit_fn("orchestrator_log", {"text": "THOUGHT: Checking tracks for approaching trains on Howrah-Chennai corridor...\n", "type": "thought"})
        emit_fn("agent_status", {"agent": "collision", "status": "running"})
        time.sleep(1.5)
        
        active_trains = self.simulator.get_all_trains() if self.simulator else []
        collision_res = self.collision_calculator.run(incident_data, active_trains)
        
        # Format collision findings
        trains_text = ""
        for t in collision_res["trains_at_risk"]:
            trains_text += f" - Train {t['train_no']} ({t['name']}): Distance {t['distance_km']}km, TTC: {t['time_to_collision_mins']} min [{t['urgency']}]\n"
            
        emit_fn("agent_status", {"agent": "collision", "status": "success", "summary": collision_res["summary"]})
        emit_fn("orchestrator_log", {"text": f"[Collision Agent Output]\n{trains_text if trains_text else ' - No trains at risk in corridor.\n'}", "type": "agent"})
        time.sleep(1.0)
        
        # 3. Signal Controller Agent
        emit_fn("orchestrator_log", {"text": "THOUGHT: Issuing stop signals to lock affected blocks and transmit emergency brakes...\n", "type": "thought"})
        emit_fn("agent_status", {"agent": "signal", "status": "running"})
        time.sleep(1.2)
        
        signal_res = self.signal_controller.run(incident_data, collision_res)
        
        # Apply emergency braking in simulation
        for cmd in signal_res["train_commands"]:
            if self.simulator:
                self.simulator.apply_emergency_braking(cmd["train_no"])
                
        # Emit signal events to update the map
        emit_fn("map_signals_updated", {"signals": signal_res["signal_commands"]})
        
        emit_fn("agent_status", {"agent": "signal", "status": "success", "summary": signal_res["summary"]})
        emit_fn("orchestrator_log", {"text": f"[Signal Agent Output] Locked {len(signal_res['signal_commands'])} block sections. Emergency braking command issued to approaching trains.\n", "type": "agent"})
        time.sleep(1.0)
        
        # 4. Rescue Coordinator Agent
        emit_fn("orchestrator_log", {"text": "THOUGHT: Safety perimeter established. Locating nearest Accident Relief Depot and alerting medical services...\n", "type": "thought"})
        emit_fn("agent_status", {"agent": "rescue", "status": "running"})
        time.sleep(1.5)
        
        rescue_res = self.rescue_coordinator.run(incident_data)
        emit_fn("agent_status", {"agent": "rescue", "status": "success", "summary": rescue_res["summary"]})
        emit_fn("orchestrator_log", {"text": f"[Rescue Agent Output] Dispatched SPART from {rescue_res['dispatch_order']['depot_name']} (ETA: {rescue_res['dispatch_order']['eta_minutes']} min). Alerted hospital: {rescue_res['hospital_alert']['hospital_name']} ({rescue_res['hospital_alert']['beds_available']} beds).\n", "type": "agent"})
        time.sleep(1.0)
        
        # 5. Communications Agent
        emit_fn("orchestrator_log", {"text": "THOUGHT: Writing alert briefings, public bulletins and loading multilingual PA announcement scripts...\n", "type": "thought"})
        emit_fn("agent_status", {"agent": "communications", "status": "running"})
        time.sleep(1.2)
        
        comm_res = self.communications.run(incident_data, collision_res, rescue_res)
        emit_fn("agent_status", {"agent": "communications", "status": "success", "summary": "Alert briefs, press release and station announcements drafted."})
        emit_fn("orchestrator_log", {"text": f"[Communications Agent Output] Hindi and English announcements compiled. DRM incident brief issued. Press notice written.\n", "type": "agent"})
        time.sleep(1.0)
        
        # Orchestrator Wrap-up
        emit_fn("orchestrator_log", {"text": "THOUGHT: Synthesis of all response telemetry complete. System returning to standby state. Incident status logged.\n", "type": "thought"})
        emit_fn("agent_status", {"agent": "orchestrator", "status": "success", "summary": "Full response pipeline successfully executed."})
        
        final_summary = {
            "incident_id": incident_id,
            "status": "COMPLETED",
            "detector": detector_res,
            "collision": collision_res,
            "signal": signal_res,
            "rescue": rescue_res,
            "communications": comm_res,
            "timestamp": datetime.now().isoformat()
        }
        
        add_decision_log(
            incident_id=incident_id,
            agent_name="ARRA Orchestrator",
            step="ORCHESTRATION_COMPLETE",
            details=final_summary,
            action_taken="ARRA completed all emergency responder dispatches and train arrests autonomously."
        )
        
        emit_fn("response_complete", final_summary)
        emit_fn("orchestrator_log", {"text": "ARRA Pipeline Execution Complete. Averted collision hazard.\n", "type": "success"})



    def _run_with_groq(self, incident_data, emit_fn):
        """Uses Groq's API to run the multi-agent tools via requests."""
        incident_id = incident_data["incident_id"]
        
        context = {
            "detector_res": None,
            "collision_res": None,
            "signal_res": None,
            "rescue_res": None,
            "communications_res": None
        }

        # Define tools executor
        def run_tool(name):
            if name == "detect_incident":
                emit_fn("orchestrator_log", {"text": "LOG: [Groq Tool Call] executing detect_incident...\n", "type": "system"})
                emit_fn("agent_status", {"agent": "detector", "status": "running"})
                time.sleep(1.0)
                res = self.detector.run(incident_data)
                context["detector_res"] = res
                emit_fn("agent_status", {"agent": "detector", "status": "success", "summary": res["summary"]})
                return res
            elif name == "calculate_collision_risk":
                emit_fn("orchestrator_log", {"text": "LOG: [Groq Tool Call] executing calculate_collision_risk...\n", "type": "system"})
                emit_fn("agent_status", {"agent": "collision", "status": "running"})
                time.sleep(1.0)
                active_trains = self.simulator.get_all_trains() if self.simulator else []
                res = self.collision_calculator.run(incident_data, active_trains)
                context["collision_res"] = res
                emit_fn("agent_status", {"agent": "collision", "status": "success", "summary": res["summary"]})
                return res
            elif name == "control_signals":
                emit_fn("orchestrator_log", {"text": "LOG: [Groq Tool Call] executing control_signals...\n", "type": "system"})
                emit_fn("agent_status", {"agent": "signal", "status": "running"})
                time.sleep(1.0)
                col_data = context["collision_res"]
                if not col_data:
                    active_trains = self.simulator.get_all_trains() if self.simulator else []
                    col_data = self.collision_calculator.run(incident_data, active_trains)
                    context["collision_res"] = col_data
                res = self.signal_controller.run(incident_data, col_data)
                context["signal_res"] = res
                for cmd in res["train_commands"]:
                    if self.simulator:
                        self.simulator.apply_emergency_braking(cmd["train_no"])
                emit_fn("map_signals_updated", {"signals": res["signal_commands"]})
                emit_fn("agent_status", {"agent": "signal", "status": "success", "summary": res["summary"]})
                return res
            elif name == "coordinate_rescue":
                emit_fn("orchestrator_log", {"text": "LOG: [Groq Tool Call] executing coordinate_rescue...\n", "type": "system"})
                emit_fn("agent_status", {"agent": "rescue", "status": "running"})
                time.sleep(1.0)
                res = self.rescue_coordinator.run(incident_data)
                context["rescue_res"] = res
                emit_fn("agent_status", {"agent": "rescue", "status": "success", "summary": res["summary"]})
                return res
            elif name == "generate_communications":
                emit_fn("orchestrator_log", {"text": "LOG: [Groq Tool Call] executing generate_communications...\n", "type": "system"})
                emit_fn("agent_status", {"agent": "communications", "status": "running"})
                time.sleep(1.0)
                col_data = context["collision_res"] or {"trains_at_risk": []}
                res_data = context["rescue_res"] or {"dispatch_order": {"depot_name": "Unknown", "eta_minutes": 99}, "hospital_alert": {"hospital_name": "Unknown", "beds_available": 0}}
                res = self.communications.run(incident_data, col_data, res_data)
                context["communications_res"] = res
                emit_fn("agent_status", {"agent": "communications", "status": "success", "summary": "Alert briefings and announcements created."})
                return res
            return None

        # Build schema
        groq_tools = [
            {
                "type": "function",
                "function": {
                    "name": "detect_incident",
                    "description": "Classifies the incident type, severity and calculates the affected track section.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_collision_risk",
                    "description": "Pulls active train positions and calculates distance/time-to-collision for trains approaching the zone.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_signals",
                    "description": "Flips track signals to RED and sends EMERGENCY_BRAKE commands to halt trains.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "coordinate_rescue",
                    "description": "Locates the nearest Accident Relief Train (ART) depot, drafts dispatch orders, and alerts hospitals.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_communications",
                    "description": "Generates DRM incident bulletins, public statements, and Hindi/English announcements.",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are ARRA, the Autonomous Railway Response Architecture orchestrator. "
                    "You have access to five tools representing safety agents. When an incident is received, "
                    "you must run them in the correct safety order to resolve it: "
                    "1. detect_incident "
                    "2. calculate_collision_risk "
                    "3. control_signals "
                    "4. coordinate_rescue "
                    "5. generate_communications "
                    "Always run all 5 agents in this exact sequence to produce a complete response. "
                    "For each tool execution, explain briefly what safety measures you are coordinating. "
                    "Once all tools are finished, write a concise final report summarizing the safety actions taken."
                )
            },
            {
                "role": "user",
                "content": f"An incident telemetry alarm has triggered. Incident data:\n{json.dumps(incident_data)}\nRun the emergency response pipeline immediately. Execute all tool operations in order."
            }
        ]

        emit_fn("orchestrator_log", {"text": "THOUGHT: Analyzing raw circuit breach via Groq API. Dispatching pipeline agents...\n", "type": "thought"})

        # Run loop
        for i in range(10):
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",  # Stable fast model on Groq
                "messages": messages,
                "tools": groq_tools,
                "tool_choice": "auto",
                "temperature": 0.2
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            res_json = response.json()
            
            choice = res_json["choices"][0]
            message = choice["message"]
            
            # OpenAI API requires message structure handling
            # Remove any None fields to be safe in the next API request
            clean_message = {
                "role": message.get("role"),
                "content": message.get("content")
            }
            if message.get("tool_calls"):
                clean_message["tool_calls"] = message.get("tool_calls")
                
            messages.append(clean_message)
            
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    
                    # Run local agent
                    tool_res = run_tool(tool_name)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps(tool_res)
                    })
                    
                    summary_text = tool_res.get("summary", f"Executed {tool_name}")
                    emit_fn("orchestrator_log", {"text": f"[Groq Tool Call Result] {summary_text}\n", "type": "agent"})
            else:
                # If no tool calls, this is the final reasoning summary response!
                final_text = message.get("content", "")
                text_lines = final_text.split("\n")
                for line in text_lines:
                    if line.strip():
                        emit_fn("orchestrator_log", {"text": f"GROQ: {line}\n", "type": "thought"})
                        time.sleep(0.1)
                break
                
        emit_fn("agent_status", {"agent": "orchestrator", "status": "success", "summary": "Orchestrator successfully resolved incident."})
        
        # Compile final outputs
        final_summary = {
            "incident_id": incident_id,
            "status": "COMPLETED",
            "detector": context["detector_res"],
            "collision": context["collision_res"],
            "signal": context["signal_res"],
            "rescue": context["rescue_res"],
            "communications": context["communications_res"],
            "timestamp": datetime.now().isoformat()
        }
        
        add_decision_log(
            incident_id=incident_id,
            agent_name="ARRA Orchestrator",
            step="ORCHESTRATION_COMPLETE",
            details=final_summary,
            action_taken="ARRA completed all emergency responses via Groq tool orchestration."
        )
        
        emit_fn("response_complete", final_summary)
        emit_fn("orchestrator_log", {"text": "ARRA Pipeline Execution Complete. Averted collision hazard.\n", "type": "success"})
