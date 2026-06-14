import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

export default function OrchestratorLog({ logs }) {
  const terminalEndRef = useRef(null);

  // Auto-scroll to bottom of terminal
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogStyle = (type) => {
    switch (type) {
      case 'thought':
        return 'text-amber-400 font-medium italic';
      case 'telemetry':
        return 'text-purple-400 font-semibold';
      case 'agent':
        return 'text-green-400 font-bold';
      case 'system':
        return 'text-cyan-400 font-mono';
      case 'warning':
        return 'text-red-400 font-semibold';
      case 'success':
        return 'text-emerald-400 font-extrabold tracking-wider';
      default:
        return 'text-gray-300';
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/90 border border-gray-800 rounded-xl overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.6)]">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-900 bg-gray-950/60">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="text-xs font-mono font-bold text-gray-400 uppercase tracking-widest">
            ARRA System Console (Live Telemetry Logs)
          </span>
        </div>
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
        </div>
      </div>

      {/* Terminal Content */}
      <div className="flex-1 p-4 font-mono text-xs overflow-y-auto min-h-[300px] max-h-[500px] space-y-2 scrollbar-thin scrollbar-thumb-gray-900 scrollbar-track-transparent">
        {logs.length === 0 ? (
          <div className="text-gray-600 italic animate-pulse">
            System idle. Awaiting track circuit failure trigger...
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className={`whitespace-pre-wrap leading-relaxed ${getLogStyle(log.type)}`}>
              <span className="text-gray-600 mr-2 selection:bg-gray-800">
                [{new Date().toLocaleTimeString()}]
              </span>
              {log.text}
            </div>
          ))
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
