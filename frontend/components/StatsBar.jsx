import { useEffect, useState } from 'react';
import { Timer, UserCheck, Flame, Zap } from 'lucide-react';

export default function StatsBar({ isRunning, startTime, endTime }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    let interval = null;
    
    if (isRunning && startTime) {
      interval = setInterval(() => {
        const now = Date.now();
        setElapsed(((now - startTime) / 1000).toFixed(1));
      }, 100);
    } else if (!isRunning && startTime && endTime) {
      setElapsed(((endTime - startTime) / 1000).toFixed(1));
    } else {
      setElapsed('0.0');
    }

    return () => clearInterval(interval);
  }, [isRunning, startTime, endTime]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 w-full bg-[#0d0d0d] border border-gray-800 rounded-xl p-4 shadow-lg mb-6">
      
      {/* Timer metric */}
      <div className="flex items-center gap-3 bg-black/40 border border-gray-900 rounded-lg p-3">
        <div className={`p-2.5 rounded-md border ${
          isRunning ? 'border-yellow-500/30 text-yellow-400 animate-pulse' : 'border-gray-800 text-gray-500'
        }`}>
          <Timer className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-gray-500">
            ARRA System Timer
          </span>
          <h2 className="text-xl font-bold font-mono text-gray-200 mt-0.5">
            {elapsed}s
          </h2>
        </div>
      </div>

      {/* Legacy Human Speed */}
      <div className="flex items-center gap-3 bg-black/40 border border-gray-900 rounded-lg p-3">
        <div className="p-2.5 rounded-md border border-gray-800 text-red-500">
          <Flame className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-gray-500">
            Manual Response Loop
          </span>
          <h2 className="text-xl font-bold font-mono text-red-500 mt-0.5">
            8 - 15 mins
          </h2>
        </div>
      </div>

      {/* ARRA Target speed */}
      <div className="flex items-center gap-3 bg-black/40 border border-gray-900 rounded-lg p-3">
        <div className="p-2.5 rounded-md border border-gray-800 text-cyan-400">
          <Zap className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-gray-500">
            ARRA Response Target
          </span>
          <h2 className="text-xl font-bold font-mono text-cyan-400 mt-0.5">
            &lt; 70 secs
          </h2>
        </div>
      </div>

      {/* Safety system multiplier */}
      <div className="flex items-center gap-3 bg-black/40 border border-gray-900 rounded-lg p-3">
        <div className="p-2.5 rounded-md border border-gray-800 text-emerald-400">
          <UserCheck className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-gray-500">
            Safety Speedup Factor
          </span>
          <h2 className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
            ~12.5x Faster
          </h2>
        </div>
      </div>

    </div>
  );
}
