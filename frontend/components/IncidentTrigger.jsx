import { useState } from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function IncidentTrigger({ onTrigger, onReset, isRunning }) {
  const [type, setType] = useState('derailment');
  const [station, setStation] = useState('BLS');
  const [severity, setSeverity] = useState(3);

  const handleNormalClick = () => {
    if (isRunning) return;
    onTrigger(type, station, parseInt(severity), false);
  };

  const handleDemoClick = () => {
    if (isRunning) return;
    onTrigger(type, station, parseInt(severity), true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleNormalClick();
  };

  return (
    <div className="bg-[#0d0d0d] border border-gray-800 rounded-xl p-4 shadow-lg w-full">
      <div className="flex items-center gap-2 border-b border-gray-900 pb-3 mb-4">
        <AlertCircle className="w-5 h-5 text-red-500 animate-pulse" />
        <h3 className="font-mono font-bold text-sm text-gray-200 uppercase tracking-wider">
          Incident Injection Terminal
        </h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 font-mono text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          
          {/* Incident Type */}
          <div>
            <label className="block text-[10px] text-gray-500 uppercase font-bold mb-1">
              Incident Type
            </label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              disabled={isRunning}
              className="w-full bg-black/60 border border-gray-800 rounded p-2 text-gray-300 focus:outline-none focus:border-red-500 disabled:opacity-50"
            >
              <option value="derailment">Derailment</option>
              <option value="obstruction">Track Obstruction</option>
              <option value="signal_failure">Signal Failure</option>
            </select>
          </div>

          {/* Station Sector */}
          <div>
            <label className="block text-[10px] text-gray-500 uppercase font-bold mb-1">
              Sector (Station)
            </label>
            <select
              value={station}
              onChange={(e) => setStation(e.target.value)}
              disabled={isRunning}
              className="w-full bg-black/60 border border-gray-800 rounded p-2 text-gray-300 focus:outline-none focus:border-red-500 disabled:opacity-50"
            >
              <option value="BLS">Balasore (BLS)</option>
              <option value="BHC">Bhadrak (BHC)</option>
              <option value="CTC">Cuttack (CTC)</option>
              <option value="RJY">Rajahmundry (RJY)</option>
              <option value="PSA">Palasa (PSA)</option>
            </select>
          </div>

          {/* Severity */}
          <div>
            <label className="block text-[10px] text-gray-500 uppercase font-bold mb-1">
              Severity Level
            </label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              disabled={isRunning}
              className="w-full bg-black/60 border border-gray-800 rounded p-2 text-gray-300 focus:outline-none focus:border-red-500 disabled:opacity-50"
            >
              <option value={3}>Level 3 (Critical)</option>
              <option value={2}>Level 2 (Major)</option>
              <option value={1}>Level 1 (Minor)</option>
            </select>
          </div>

        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2 items-start sm:items-stretch">
          
          <button
            type="button"
            onClick={handleNormalClick}
            disabled={isRunning}
            className={`flex-1 font-bold tracking-widest text-[10px] sm:text-xs uppercase py-3 px-4 rounded-lg border transition-all duration-300 flex items-center justify-center gap-2 ${
              isRunning
                ? 'bg-red-950/20 border-red-900/40 text-red-700/60 cursor-not-allowed'
                : 'bg-red-600 border-red-500 hover:bg-red-700 text-white shadow-[0_0_20px_rgba(239,68,68,0.3)] hover:shadow-[0_0_25px_rgba(239,68,68,0.5)] active:scale-[0.98] cursor-pointer'
            }`}
          >
            <span className={isRunning ? '' : 'animate-ping inline-flex h-2 w-2 rounded-full bg-white opacity-75 mr-1'}></span>
            {isRunning ? 'Responding...' : 'TRIGGER AUTONOMOUS RESPONSE'}
          </button>

          <div className="flex-1 flex flex-col gap-1 w-full">
            <button
              type="button"
              onClick={handleDemoClick}
              disabled={isRunning}
              className={`w-full font-bold tracking-widest text-[10px] sm:text-xs uppercase py-3 px-4 rounded-lg border transition-all duration-300 flex items-center justify-center gap-2 ${
                isRunning
                  ? 'bg-amber-950/20 border-amber-900/40 text-amber-700/60 cursor-not-allowed'
                  : 'bg-amber-500 border-amber-400 hover:bg-amber-600 text-black shadow-[0_0_20px_rgba(245,158,11,0.2)] hover:shadow-[0_0_25px_rgba(245,158,11,0.4)] active:scale-[0.98] cursor-pointer'
              }`}
            >
              DEMO MODE
            </button>
            <span className="text-[9px] text-gray-500 text-center font-mono italic">
              Guaranteed collision scenario
            </span>
          </div>

          <button
            type="button"
            onClick={onReset}
            className="bg-gray-900 border border-gray-800 hover:border-gray-700 hover:bg-gray-800 text-gray-400 py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 active:scale-[0.98] cursor-pointer font-bold text-[10px] sm:text-xs"
          >
            <RotateCcw className="w-4 h-4" />
            RESET SYSTEM
          </button>

        </div>
      </form>
    </div>
  );
}
