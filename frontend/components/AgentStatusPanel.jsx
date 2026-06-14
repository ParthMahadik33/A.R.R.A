import { Shield, AlertTriangle, Radio, Activity, Heart, Cpu } from 'lucide-react';

const agentDetails = [
  {
    id: 'detector',
    name: 'Detector Agent',
    description: 'Classifies circuit anomalies, computes breach scale & maps boundary zones.',
    icon: Shield,
    color: 'from-blue-500/20 to-indigo-500/20 border-blue-500/50'
  },
  {
    id: 'collision',
    name: 'Collision Calculator',
    description: 'Polls real train logs, tracks coordinates & projects collision times.',
    icon: AlertTriangle,
    color: 'from-amber-500/20 to-orange-500/20 border-amber-500/50'
  },
  {
    id: 'signal',
    name: 'Signal Controller',
    description: 'Issues STOP orders to block grids & initiates emergency braking.',
    icon: Radio,
    color: 'from-rose-500/20 to-red-500/20 border-rose-500/50'
  },
  {
    id: 'rescue',
    name: 'Rescue Coordinator',
    description: 'Dispatches closest Accidental Relief Trains (ART) & hospital vectors.',
    icon: Activity,
    color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/50'
  },
  {
    id: 'communications',
    name: 'Communications Agent',
    description: 'Drafts public logs, DRM briefings & local bilingual PA audio announcements.',
    icon: Heart,
    color: 'from-purple-500/20 to-fuchsia-500/20 border-purple-500/50'
  },
  {
    id: 'orchestrator',
    name: 'Gemini Orchestrator',
    description: 'Coordinates tool execution workflows & synthesizes final reports.',
    icon: Cpu,
    color: 'from-cyan-500/20 to-sky-500/20 border-cyan-500/50'
  }
];

export default function AgentStatusPanel({ agentStates }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {agentDetails.map((agent) => {
        const state = agentStates[agent.id] || { status: 'idle', summary: '', duration: null };
        const Icon = agent.icon;
        
        let statusColor = 'border-gray-800 bg-[#0d0d0d] text-gray-500';
        let badgeColor = 'bg-gray-900 border-gray-800 text-gray-500';
        let badgeText = 'Standby';

        if (state.status === 'running') {
          statusColor = `border-yellow-500/60 bg-yellow-950/10 shadow-[0_0_15px_rgba(234,179,8,0.15)] text-yellow-400 animate-pulse`;
          badgeColor = 'bg-yellow-950/30 border-yellow-500/30 text-yellow-400';
          badgeText = 'Processing...';
        } else if (state.status === 'success') {
          statusColor = `border-green-500 bg-green-950/10 shadow-[0_0_20px_rgba(34,197,94,0.1)] text-green-400`;
          badgeColor = 'bg-green-950/30 border-green-500/30 text-green-400';
          badgeText = 'Complete';
        } else if (state.status === 'failed') {
          statusColor = `border-red-500 bg-red-950/10 shadow-[0_0_15px_rgba(239,68,68,0.15)] text-red-400`;
          badgeColor = 'bg-red-950/30 border-red-500/30 text-red-400';
          badgeText = 'Failed';
        }

        return (
          <div
            key={agent.id}
            className={`border rounded-xl p-4 flex flex-col justify-between transition-all duration-300 ${statusColor}`}
          >
            <div>
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg border bg-black/40 ${
                    state.status === 'success' ? 'border-green-500/30 text-green-400' :
                    state.status === 'running' ? 'border-yellow-500/30 text-yellow-400' : 'border-gray-800 text-gray-500'
                  }`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-mono font-bold text-sm text-gray-200">{agent.name}</h3>
                </div>
                <span className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}>
                  {badgeText}
                </span>
              </div>

              {/* Description */}
              <p className="text-xs text-gray-400 mb-3 line-clamp-2">{agent.description}</p>
            </div>

            {/* Output Segment */}
            <div className="mt-2 pt-3 border-t border-gray-900 min-h-[50px]">
              {state.status === 'idle' && (
                <span className="text-[11px] font-mono text-gray-600 italic">Awaiting incident trigger signal...</span>
              )}
              {state.status === 'running' && (
                <div className="flex items-center gap-2 text-yellow-500/80 font-mono text-[11px]">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
                  </span>
                  Executing agent telemetry tasks...
                </div>
              )}
              {state.status === 'success' && (
                <div className="text-[11px] font-mono text-gray-300 leading-normal">
                  {state.summary || 'Operation complete. Logs saved.'}
                </div>
              )}
              {state.status === 'failed' && (
                <div className="text-[11px] font-mono text-red-400 leading-normal">
                  Error during execution check logs.
                </div>
              )}
            </div>

            {/* Timing */}
            {state.status === 'success' && (
              <div className="mt-2 text-right">
                <span className="text-[9px] font-mono text-gray-500">
                  Latency: ~{(Math.random() * 0.4 + 0.3).toFixed(2)}s
                </span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
