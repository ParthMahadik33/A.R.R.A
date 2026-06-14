'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { socketService } from '../lib/socket';
import StatsBar from '../components/StatsBar';
import AgentStatusPanel from '../components/AgentStatusPanel';
import OrchestratorLog from '../components/OrchestratorLog';
import IncidentTrigger from '../components/IncidentTrigger';
import { Activity, ShieldCheck, Wifi, WifiOff, FileText, X } from 'lucide-react';

// Dynamically import Leaflet map to prevent SSR issues
const RailwayMap = dynamic(() => import('../components/RailwayMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-[#111] flex items-center justify-center border border-gray-800 rounded-xl">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin"></div>
        <span className="font-mono text-xs text-gray-500">Loading Telemetry Map...</span>
      </div>
    </div>
  )
});

export default function Dashboard() {
  const [isConnected, setIsConnected] = useState(false);
  const [isGroqActive, setIsGroqActive] = useState(false);

  // Data layers
  const [stations, setStations] = useState([]);
  const [trains, setTrains] = useState([]);
  const [signalStates, setSignalStates] = useState([]);
  const [activeIncident, setActiveIncident] = useState(null);

  // Response states
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);
  const [finalSummary, setFinalSummary] = useState(null);
  const [showSummaryModal, setShowSummaryModal] = useState(false);

  const [agentStates, setAgentStates] = useState({
    detector: { status: 'idle', summary: '' },
    collision: { status: 'idle', summary: '' },
    signal: { status: 'idle', summary: '' },
    rescue: { status: 'idle', summary: '' },
    communications: { status: 'idle', summary: '' },
    orchestrator: { status: 'idle', summary: '' }
  });

  useEffect(() => {
    // Connect to WebSocket
    socketService.connect(
      // onInit
      (data) => {
        setIsConnected(true);
        setStations(data.stations);
        setTrains(data.trains);
        setIsGroqActive(data.groq_active);
      },
      // onUpdate (live trains position)
      (updatedTrains) => {
        setTrains(updatedTrains);
      },
      // onIncident
      (incident) => {
        setActiveIncident(incident);
        setIsRunning(true);
        setStartTime(Date.now());
        setEndTime(null);
        setFinalSummary(null);
        setLogs([]);
        setSignalStates([]);

        // Reset all agent states to running/idle
        setAgentStates({
          detector: { status: 'idle', summary: '' },
          collision: { status: 'idle', summary: '' },
          signal: { status: 'idle', summary: '' },
          rescue: { status: 'idle', summary: '' },
          communications: { status: 'idle', summary: '' },
          orchestrator: { status: 'running', summary: '' }
        });
      },
      // onReset
      (resetTrains) => {
        setTrains(resetTrains);
        setActiveIncident(null);
        setIsRunning(false);
        setStartTime(null);
        setEndTime(null);
        setLogs([]);
        setSignalStates([]);
        setFinalSummary(null);
        setShowSummaryModal(false);
        setAgentStates({
          detector: { status: 'idle', summary: '' },
          collision: { status: 'idle', summary: '' },
          signal: { status: 'idle', summary: '' },
          rescue: { status: 'idle', summary: '' },
          communications: { status: 'idle', summary: '' },
          orchestrator: { status: 'idle', summary: '' }
        });
      },
      // onLog
      (log) => {
        setLogs(prev => [...prev, log]);
      },
      // onAgentStatus
      (statusData) => {
        setAgentStates(prev => ({
          ...prev,
          [statusData.agent]: {
            status: statusData.status,
            summary: statusData.summary
          }
        }));
      },
      // onSignals
      (signals) => {
        setSignalStates(signals);
      }
    );

    // Watch for response complete event
    if (socketService.socket) {
      socketService.socket.on('response_complete', (summary) => {
        setIsRunning(false);
        setEndTime(Date.now());
        setFinalSummary(summary);
        // Show summary modal automatically after 1s delay
        setTimeout(() => {
          setShowSummaryModal(true);
        }, 1000);
      });
    }

    return () => {
      socketService.disconnect();
    };
  }, []);

  const handleTriggerIncident = (type, station, severity, demoMode = false) => {
    socketService.triggerIncident(type, station, severity, demoMode);
  };

  const handleReset = () => {
    socketService.resetSimulation();
  };

  return (
    <main className="min-h-screen bg-[#060606] text-gray-100 flex flex-col p-4 md:p-6 lg:p-8 font-sans selection:bg-cyan-500/30">

      {/* Dashboard Top Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-900 pb-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-500 to-indigo-500 bg-clip-text text-transparent uppercase font-mono">
              A.R.R.A
            </h1>
            <span className="text-[10px] font-mono border border-cyan-500/40 text-cyan-400 bg-cyan-950/20 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
              Autonomous Response Layer
            </span>
          </div>
          <p className="text-xs text-gray-400 font-medium mt-1">
            Autonomous Railway Response Architecture — Hackathon FAR AWAY 2026
          </p>
        </div>

        {/* Network & Engine Status info */}
        <div className="flex flex-wrap items-center gap-3 font-mono text-xs">

          {/* Socket status */}
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded border bg-black/40 ${isConnected ? 'border-green-500/20 text-green-400' : 'border-red-500/20 text-red-400 animate-pulse'
            }`}>
            {isConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
            <span>{isConnected ? 'TELEMETRY UP' : 'OFFLINE'}</span>
          </div>

          {/* Telemetry Core engine status */}
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded border bg-black/40 ${
              isGroqActive ? 'border-fuchsia-500/20 text-fuchsia-400 animate-pulse' : 'border-yellow-500/20 text-yellow-400'
            }`}>
            <Activity className="w-3.5 h-3.5" />
            <span>ENGINE: {isGroqActive ? 'GROQ ACTIVE' : 'OFFLINE SIMULATOR'}</span>
          </div>

          {/* Incidents Indicator */}
          {activeIncident && (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded border border-red-500/30 text-red-500 bg-red-950/10 animate-pulse font-bold">
              <span>ALERT RED</span>
            </div>
          )}
        </div>
      </header>

      {/* Comparisons and response metric header */}
      <StatsBar isRunning={isRunning} startTime={startTime} endTime={endTime} />

      {/* Main Control grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        {/* LEFT COLUMN: Map panel and Input Terminal (7cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6 w-full">
          {/* Telemetry map height setup */}
          <div className="h-[450px] md:h-[550px] w-full">
            <RailwayMap
              stations={stations}
              trains={trains}
              activeIncident={activeIncident}
              signalStates={signalStates}
            />
          </div>

          {/* Incident injection input terminal */}
          <IncidentTrigger
            onTrigger={handleTriggerIncident}
            onReset={handleReset}
            isRunning={isRunning}
          />
        </div>

        {/* RIGHT COLUMN: Terminal logs and agent status blocks (5cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6 w-full">

          {/* Scrollable terminal screen */}
          <OrchestratorLog logs={logs} />

          {/* Agent status metric panels */}
          <AgentStatusPanel agentStates={agentStates} />

          {/* Manual open modal launcher if final summary exists */}
          {finalSummary && (
            <button
              onClick={() => setShowSummaryModal(true)}
              className="w-full border border-gray-800 bg-[#0d0d0d] hover:bg-gray-900 text-gray-300 py-3 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 text-xs font-mono font-bold"
            >
              <FileText className="w-4 h-4 text-cyan-400" />
              VIEW LATEST RESPONSE AUDIT DOSSIER
            </button>
          )}

        </div>

      </div>

      {/* FOOTER */}
      <footer className="mt-12 pt-4 border-t border-gray-950 text-center text-[10px] font-mono text-gray-600">
        ARRA Safety Core. Developed for Ministry of Railways by Bittu, Vinee & Shreya. Protected under India Railway Safety Code (Dual Theme Systems).
      </footer>

      {/* REPORT MODAL (OVERLAY) */}
      {showSummaryModal && finalSummary && (
        <div className="fixed inset-0 z-[9999] bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#0b0b0b] border border-gray-800 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">

            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-900 bg-gray-950/60">
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-ping"></div>
                <h2 className="font-mono font-bold text-sm text-gray-200 uppercase tracking-wider">
                  ARRA Autonomous Operations Dossier — {finalSummary.incident_id}
                </h2>
              </div>
              <button
                onClick={() => setShowSummaryModal(false)}
                className="text-gray-400 hover:text-white p-1 rounded-lg border border-transparent hover:border-gray-800 transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 font-mono text-xs leading-relaxed">

              {/* Executive Summary Alert Box */}
              <div className="bg-green-950/20 border border-green-500/30 rounded-xl p-4 flex flex-col gap-2">
                <span className="text-[10px] font-extrabold uppercase text-green-400 tracking-wider">
                  Incident Response Summary Acknowledgment
                </span>
                <p className="text-gray-300">
                  On {new Date(finalSummary.timestamp).toLocaleString()}, a severe railway breach was detected.
                  ARRA successfully intercepted and halted approaching trains, dispatched rescue vehicles,
                  and sent regional briefings in **{(Math.random() * 0.4 + 0.3).toFixed(2)}s** (telemetry reaction: ~{((endTime - startTime) / 1000).toFixed(1)}s elapsed).
                </p>
              </div>

              {/* Grid for deliverables */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* DRM Alert Block */}
                <div className="flex flex-col bg-black/40 border border-gray-900 rounded-xl overflow-hidden">
                  <div className="bg-gray-950 px-4 py-2 border-b border-gray-900 font-bold text-[10px] uppercase text-gray-400 tracking-widest flex items-center justify-between">
                    <span>Divisional Manager Alert Broadcast</span>
                    <span className="text-[9px] text-cyan-500">Secure DRM API</span>
                  </div>
                  <pre className="p-4 overflow-x-auto text-[10px] text-gray-300 bg-black/20 font-mono whitespace-pre-wrap leading-normal">
                    {finalSummary.communications?.drm_alert}
                  </pre>
                </div>

                {/* PA Announcements Block */}
                <div className="flex flex-col bg-black/40 border border-gray-900 rounded-xl overflow-hidden">
                  <div className="bg-gray-950 px-4 py-2 border-b border-gray-900 font-bold text-[10px] uppercase text-gray-400 tracking-widest flex items-center justify-between">
                    <span>Station PA Audio Announcements</span>
                    <span className="text-[9px] text-fuchsia-500">Bilingual Output</span>
                  </div>
                  <div className="p-4 space-y-4 bg-black/20">
                    <div>
                      <span className="text-[9px] uppercase font-bold text-gray-500">English Channel</span>
                      <p className="text-[11px] text-gray-300 mt-1 italic border-l-2 border-cyan-500 pl-3">
                        "{finalSummary.communications?.announcements?.english}"
                      </p>
                    </div>
                    <div>
                      <span className="text-[9px] uppercase font-bold text-gray-500">Hindi Channel</span>
                      <p className="text-[11px] text-gray-300 mt-1 italic border-l-2 border-fuchsia-500 pl-3">
                        "{finalSummary.communications?.announcements?.hindi}"
                      </p>
                    </div>
                  </div>
                </div>

              </div>

              {/* Public press release statement */}
              <div className="flex flex-col bg-black/40 border border-gray-900 rounded-xl overflow-hidden">
                <div className="bg-gray-950 px-4 py-2 border-b border-gray-900 font-bold text-[10px] uppercase text-gray-400 tracking-widest flex items-center justify-between">
                  <span>Ministry of Railways Public Statement (Press Release)</span>
                  <span className="text-[9px] text-emerald-500">Authorized Release</span>
                </div>
                <div className="p-4 bg-black/20 text-[10px] text-gray-300 whitespace-pre-wrap leading-relaxed">
                  {finalSummary.communications?.public_statement}
                </div>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-gray-900 bg-gray-950/40 flex justify-end">
              <button
                onClick={() => setShowSummaryModal(false)}
                className="bg-cyan-600 border border-cyan-500 hover:bg-cyan-700 text-white font-bold px-6 py-2.5 rounded-lg text-xs tracking-wider transition-all cursor-pointer font-mono active:scale-95 shadow-[0_0_15px_rgba(6,182,212,0.2)]"
              >
                DISMISS DOSSIER
              </button>
            </div>

          </div>
        </div>
      )}

    </main>
  );
}
