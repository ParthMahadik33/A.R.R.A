import { io } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';

class SocketService {
  constructor() {
    this.socket = null;
  }

  connect(onInit, onUpdate, onIncident, onReset, onLog, onAgentStatus, onSignals) {
    if (this.socket) return;

    this.socket = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
    });

    this.socket.on('connect', () => {
      console.log('Connected to ARRA WebSocket backend');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from ARRA WebSocket backend');
    });

    this.socket.on('init_data', (data) => {
      if (onInit) onInit(data);
    });

    this.socket.on('trains_update', (data) => {
      if (onUpdate) onUpdate(data.trains);
    });

    this.socket.on('incident_triggered', (data) => {
      if (onIncident) onIncident(data);
    });

    this.socket.on('simulation_reset', (data) => {
      if (onReset) onReset(data.trains);
    });

    this.socket.on('orchestrator_log', (data) => {
      if (onLog) onLog(data);
    });

    this.socket.on('agent_status', (data) => {
      if (onAgentStatus) onAgentStatus(data);
    });

    this.socket.on('map_signals_updated', (data) => {
      if (onSignals) onSignals(data.signals);
    });
  }

  triggerIncident(type, station, severity, demoMode = false) {
    if (this.socket) {
      this.socket.emit('trigger_incident', { type, station, severity, demo_mode: demoMode });
    }
  }

  resetSimulation() {
    if (this.socket) {
      this.socket.emit('reset_simulation');
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export const socketService = new SocketService();
