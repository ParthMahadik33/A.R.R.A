# ARRA — Autonomous Railway Response Architecture

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange?style=flat-square)](https://groq.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Socket.io-blueviolet?style=flat-square&logo=socketdotio&logoColor=white)](https://socket.io/)

> **Autonomous Incident Response Layer for Indian Railways**  
> Developed for **FAR AWAY 2026** — India's Biggest International Hackathon  
> Theme: *Railways* + *Agentic & Autonomous Systems* (Dual Theme)  
> Team: **Synapse**  
> Live Website: [arraproject.netlify.app](https://arraproject.netlify.app/)

---

## The Problem

On June 2nd, 2023, the Balasore triple-train collision resulted in 293 fatalities. The Coromandel Express derailed, spilling wreckage onto the adjacent track; 120 seconds later, the oncoming Yeshvantpur Express collided with the debris. Of the 293 total deaths, 261 occurred during this second impact. The manual safety coordination pipeline—requiring sequential phone communication between station masters, section controllers, and traction controllers—consumed 14 minutes to coordinate a response. There was no autonomous software layer integrated with the existing track circuits to process telemetry faults and immediately execute emergency halting protocols.

---

## The Solution

**ARRA (Autonomous Railway Response Architecture)** provides that immediate, autonomous safety reaction layer. By linking track circuit telemetry directly to a six-agent reasoning system, ARRA intercepts incoming hazards and coordinates a complete regional response in **under 70 seconds**—representing a **12.5x speedup** that eliminates human coordination latency. The system detects track circuit failures, calculates kinematics-based collision risks, triggers block-level signal changes to RED, transmits emergency braking orders directly to locomotives, dispatches Accident Relief Trains (ART) with local hospital vectors, and compiles bilingual public and administrative notifications.

---

## Demo

**Live Website:** [arraproject.netlify.app](https://arraproject.netlify.app/)

[![ARRA Demo Video](https://img.shields.io/badge/Demo--Video-Watch%20Now-red?style=for-the-badge&logo=youtube)](YOUR_VIDEO_URL_HERE)

*(Judges: Please watch the demo video first to see ARRA in action. You can also interact with the live dashboard on the netlify deployment).*

---

## How It Works

ARRA uses a multi-agent workflow coordinated by an Orchestrator. When a track circuit breach occurs, the agents run in sequence to isolate the incident and coordinate the response:

*   **[DetectorAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/detector.py#L4)**: Classifies the telemetry fault type (derailment, obstruction, signal failure), assigns severity (levels 1-3), and maps the affected track block section boundaries.
*   **[CollisionCalculatorAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/collision.py#L5)**: Evaluates real-time train positions, directions, and velocities along the Howrah-Chennai corridor to compute Time-to-Collision (TTC) physics, handling double-track blockages for derailments (Severity 3).
*   **[SignalControllerAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/signal.py#L4)**: Fails signals to RED at 2km block intervals across a 10km protection zone and issues emergency braking orders directly to approaching critical and warning trains.
*   **[RescueCoordinatorAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/rescue.py#L20)**: Identifies the nearest Accident Relief Train (ART) depot using great-circle haversine calculations, estimates response ETAs based on a 60 km/h travel speed plus a 15-minute turnout protocol, and secures trauma bed capacity at the closest district hospital.
*   **[CommunicationsAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/communications.py#L5)**: Compiles formatted DRM alerts, official press releases, and bilingual English/Hindi station public announcements simultaneously.
*   **[ArraOrchestrator](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/orchestrator.py#L13)**: Chains the agentic tool workflow using Gemini 2.0 Flash and Groq Llama 3.3 function calling, publishing structured logs and statuses in real time.

```
                       [Track Circuit Breach Telemetry]
                                      |
                                      v
                        +---------------------------+
                        |     ARRA Orchestrator     |
                        | (Gemini 2.0 / Llama 3.3)  |
                        +-------------+-------------+
                                      |
         +----------------------------+----------------------------+
         | (1) Tool Call              | (2) Tool Call              | (3) Tool Call
         v                            v                            v
  +--------------+             +--------------+             +--------------+
  |   Detector   |             |  Collision   |             |    Signal    |
  |    Agent     |             |  Calculator  |             |  Controller  |
  +------+-------+             +------+-------+             +------+-------+
         |                            |                            |
         | Returns Zone/Severity      | Returns TTC Risk Matrix    | Commands Stop & Brakes
         +----------------------------+----------------------------+
                                      |
                                      v
                        +---------------------------+
                        |     ARRA Orchestrator     |
                        +-------------+-------------+
                                      |
         +----------------------------+----------------------------+
         | (4) Tool Call                                           | (5) Tool Call
         v                                                         v
  +--------------+                                          +--------------+
  |    Rescue    |                                          |Communications|
  | Coordinator  |                                          |    Agent     |
  +------+-------+                                          +------+-------+
         |                                                         |
         | Dispatches ART & Hospitals                              | Generates PA/DRM Alerts
         +----------------------------+----------------------------+
                                      |
                                      v
                        +---------------------------+
                        |  Synthesized Dossier &    |
                        |   Real-time WebSockets    |
                        +-------------+-------------+
                                      |
                      +---------------+---------------+
                      |                               |
                      v                               v
            +-------------------+           +-------------------+
            | SQLite DB Log     |           | Next.js Dashboard |
            | (Auditable Audit) |           | (Interactive Map) |
            +-------------------+           +-------------------+
```

---

## Technical Depth

This section details the specific algorithms and kinematics equations implemented across the agents.

### 1. Great-Circle Distance Calculation (Haversine Formula)
Implemented in [haversine](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/rescue.py#L8) to compute geographical distances between the incident site and depots/hospitals:

```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
```

### 2. Accident Relief Train (ART) and Hospital Emergency ETA Calculations
Used by [RescueCoordinatorAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/rescue.py#L20) to generate realistic dispatch logistics matching Indian Railways emergency SOPs:

$$\text{ETA}_{\text{ART}} = \left( \frac{\text{Distance}_{\text{depot}}}{\text{Speed}_{\text{ART}}} \times 60 \right) + T_{\text{turnout\_day}}$$

$$\text{ETA}_{\text{Ambulance}} = \left( \frac{\text{Distance}_{\text{hospital}}}{\text{Speed}_{\text{ambulance}}} \times 60 \right) + T_{\text{dispatch\_hosp}}$$

*Parameters:*
*   $\text{Speed}_{\text{ART}} = 60.0 \text{ km/h}$
*   $T_{\text{turnout\_day}} = 15.0 \text{ minutes}$ (standard daytime mobilization constraint)
*   $\text{Speed}_{\text{ambulance}} = 50.0 \text{ km/h}$
*   $T_{\text{dispatch\_hosp}} = 5.0 \text{ minutes}$

### 3. Kinematic Collision Risk and Time-to-Collision (TTC)
Computed by [CollisionCalculatorAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/collision.py#L5) for each active train on the corridor:
*   Let $D$ be the distance to the incident marker ($KM_{\text{incident}}$) in km.
*   Let $V$ be the current speed in km/h.
*   If the train is approaching the block:
$$\text{TTC} = \left( \frac{D}{V} \right) \times 60 \text{ minutes}$$
*   Risk Classifications:
    *   $\text{TTC} \le 3.0 \text{ mins} \rightarrow \text{CRITICAL}$
    *   $\text{TTC} \le 8.0 \text{ mins} \rightarrow \text{WARNING}$
    *   $\text{TTC} \le 15.0 \text{ mins} \rightarrow \text{MONITOR}$
    *   $\text{TTC} > 15.0 \text{ mins} \rightarrow \text{SAFE}$
*   In a derailment (Severity 3), the agent calculates a bidirectional track hazard blocking both UP and DOWN lines, modeling the exact failure mode at Balasore.

### 4. Absolute Block Signaling Spacing and Safeguard Zone
The [SignalControllerAgent](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/agents/signal.py#L4) simulates absolute block locking intervals:
*   Lock Radius: $\pm 5.0 \text{ km}$ surrounding $KM_{\text{incident}}$, establishing a 10km security buffer.
*   Override Frequency: Signals are targeted at every 2.0 km interval.
*   Command Protocol: All signals within the buffer range are set to `STOP` (RED), and an `EMERGENCY_BRAKE` order is transmitted.

### 5. Rolling Stock Inertia and Deceleration Profile
Simulated inside [TrainSimulator](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/backend/data/simulation.py#L101) to replicate realistic train deceleration:

$$V_{t + \Delta t} = \max\left(V_{\text{target}}, V_t - a_{\text{decel}} \cdot \Delta t\right)$$

*Deceleration rates:*
*   Emergency braking: $a_{\text{decel}} = 25 \text{ km/h/s}$ (approx. $0.69 \text{ m/s}^2$ average deceleration)
*   Normal braking: $a_{\text{decel}} = 10 \text{ km/h/s}$

---

## Tech Stack

| Layer | Technology | Details / Purpose |
|---|---|---|
| **Frontend** | Next.js 14 | High-performance client-side rendering with Tailwind CSS styling |
| **Mapping Engine** | Leaflet.js + OpenStreetMap | Interactive, real-time spatial positioning of rolling stock |
| **Real-time Comms** | Socket.IO | Persistent full-duplex WebSockets streaming agent telemetry and logs |
| **Backend Framework**| Python Flask + Flask-SocketIO | Lightweight asynchronous Python server running background thread simulation |
| **Orchestration** | Groq Llama 3.3 / Gemini 2.0 Flash | Agentic reasoning using OpenAI-compatible function calling API schemas |
| **Database** | SQLite | Server-side event sourcing and structured audit logs |
| **Simulation Core** | Python Threading | Asynchronous physics-based kinematic tracking updated every 2.0 seconds |

---

## Setup and Installation

Follow these steps to run the complete ARRA backend and frontend locally:

### Prerequisites
*   Node.js (v20+ recommended)
*   Python (3.10+ recommended)

### 1. Environmental Configuration
Clone the repository and create a [.env](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/.env) file in the root workspace directory:

```bash
git clone https://github.com/ParthMahadik33/A.R.R.A.git
cd A.R.R.A
```

Create [.env](file:///c:/Users/Dell/OneDrive/文档/A.R.R.A%201/.env):
```env
# ARRA System Environment Configuration
GEMINI_API_KEY="your-google-ai-studio-api-key-here"
GROQ_API_KEY="your-groq-api-key-here"
PORT=5000
HOST=127.0.0.1
```
*(If Gemini rate limits or fails, the orchestrator redirects to the Groq API. If both keys are absent, ARRA defaults to its offline autonomous rule-based simulation engine so it remains 100% testable).*

### 2. Backend Server Setup
In a terminal, navigate to the root directory and set up the Python environment:
```bash
# Set up virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the backend Flask-SocketIO server
python backend/main.py
```
The Flask backend will launch at `http://127.0.0.1:5000`. It will initialize the SQLite database at `backend/db/arra.db` and start simulated train telemetry movements.

### 3. Frontend Dashboard Setup
In a separate terminal, navigate to the `frontend` directory and set up the Next.js client:
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser to access the live operations telemetry dashboard.

---

## How to Run the Demo

1.  **Corridor Monitoring:** Start page to inspect the Live Railway Corridor Map with real-time train positions. Signals are Green.
2.  **Arm Sensors:** Click the **ARM SENSORS** button to initiate an 8-second countdown simulating real-time telemetry monitoring.
3.  **Trigger Incident (Demo Mode):** Toggle the **DEMO MODE** option (which positions at least one train in the warning/critical range to demonstrate active threat mitigation) and select an incident location (e.g. Balasore/BLS, derailment, severity 3). Trigger the incident.
4.  **Observe Response:** Watch the terminal interface showing the streaming orchestrator logs, and note that the signals on the map flip to RED. Critical and warning trains will decelerate and stop safely.
5.  **Dossier Generation:** Once complete, the ARRA Autonomous Operations Dossier modal automatically appears, displaying ready-to-dispatch DRM alerts (with train numbers, locations, and ETAs), bilingual Hindi/English PA announcements, and official Ministry of Railways press releases.
6.  **Timer and Reset:** Review the dashboard execution timer to confirm the pipeline resolved the incident in under 70 seconds (as opposed to the 14-minute manual baseline). Press the reset button to return the simulator to standby.

---

## Technology Readiness Level (TRL)

**Current Status: TRL 4 (Component and/or breadboard validation in laboratory environment)**

The ARRA prototype integrates all six operational agents using authentic mathematical routing, block signal intervals, and deceleration physics. The orchestrator maps and runs on actual geographic coordinates of the Howrah-Chennai mainline using real historical schedule data.

---

## Real World Deployment Path

To transition the ARRA simulation system into a production-grade safety environment, the following engineering steps must be executed:

1.  **Telemetry & Sensor Integration**: Replace the simulated background thread with direct integrations into Indian Railways' solid-state electronic interlocking systems (EI), digital axle counters (DAC), and track circuit relays.
2.  **Interlocking System Integration**: Interface the Signal Controller with safety-critical wayside signaling systems (EI/PI) using failsafe relays to execute signal state changes autonomously.
3.  **Locomotive Braking Systems**: Connect directly to Kavach (Indian Railways' ATP system) or onboard Train Collision Avoidance System (TCAS) to transmit direct brake-application signals via GSM-R or LTE-R.
4.  **Official API Connections**: Replace simulated schedules with live streams from the National Train Enquiry System (NTES) API and COA (Control Office Application).
5.  **Emergency Response Networks**: Wire the dispatch systems directly to NDRF, local District Disaster Management Authorities (DDMA), and the railway division's ART paging systems.

---

## Team

Developed by **Synapse** for **FAR AWAY 2026** — India's Biggest International Hackathon.
