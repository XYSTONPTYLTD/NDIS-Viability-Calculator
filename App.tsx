
import React, { useState, useEffect } from 'react';
import { ClientData, AnalysisResult, SupportLevel } from './types';
import { DEFAULTS, SUPPORT_OPTIONS } from './constants';
import { calculateViability } from './utils/ndis';
import { PieChart, TrajectoryChart } from './components/Charts';
import { getGeminiAnalysis } from './services/geminiService';

function App() {
  // Default Dates
  const today = new Date();
  const defaultStart = new Date(today);
  defaultStart.setDate(today.getDate() - 84); // 12 weeks ago
  const defaultEnd = new Date(today);
  defaultEnd.setDate(today.getDate() + 280); // 40 weeks future

  // State
  const [data, setData] = useState<ClientData>(() => {
    const saved = localStorage.getItem('ndis-fail-safe-v2');
    return saved ? JSON.parse(saved) : {
      supportLevel: "Level 2: Coordination of Supports",
      hourlyRate: DEFAULTS.HOURLY_RATE,
      timeInputMode: DEFAULTS.TIME_INPUT_MODE,
      planStartDate: defaultStart.toISOString().split('T')[0],
      planEndDate: defaultEnd.toISOString().split('T')[0],
      manualWeeksRemaining: DEFAULTS.MANUAL_WEEKS,
      totalBudget: DEFAULTS.TOTAL_BUDGET,
      currentBalance: DEFAULTS.CURRENT_BALANCE,
      hoursPerWeek: DEFAULTS.HOURS_PER_WEEK
    };
  });

  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string>("");
  const [loadingAi, setLoadingAi] = useState(false);
  const [showDisclaimer, setShowDisclaimer] = useState(false);

  useEffect(() => {
    localStorage.setItem('ndis-fail-safe-v2', JSON.stringify(data));
    setResults(calculateViability(data));
    setAiAnalysis(""); // Clear old analysis on change
  }, [data]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'supportLevel') {
      const rate = SUPPORT_OPTIONS[value as SupportLevel];
      setData(prev => ({ ...prev, supportLevel: value as SupportLevel, hourlyRate: rate }));
    } else if (name === 'planStartDate' || name === 'planEndDate') {
      setData(prev => ({ ...prev, [name]: value }));
    } else if (name === 'timeInputMode') {
      // When switching modes, we prefer to keep the underlying data consistent if possible,
      // but for now we just toggle the mode view.
      setData(prev => ({ ...prev, timeInputMode: value as 'dates' | 'weeks' }));
    } else {
      const num = parseFloat(value);
      setData(prev => ({ ...prev, [name]: isNaN(num) ? 0 : num }));
    }
  };

  const handleAskAI = async () => {
    if (!results) return;
    setLoadingAi(true);
    const analysis = await getGeminiAnalysis(data, results);
    setAiAnalysis(analysis);
    setLoadingAi(false);
  };

  if (!results) return <div className="text-white p-10">Initializing Fail-Safe Calculator...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-inter selection:bg-blue-500 selection:text-white">
      
      {/* HEADER */}
      <header className="bg-slate-900 border-b border-slate-800 p-4 md:p-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-black tracking-tighter text-white flex items-center gap-2">
              <span>🛡️</span> NDIS Viability Master <span className="text-blue-400 font-normal text-lg">(Fail-Safe)</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">The Zero-Guessing Tool for Independent Coordinators.</p>
          </div>
          <div className="hidden md:block text-right">
             <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Today's Date</div>
             <div className="text-xl font-mono font-bold text-slate-200">
               {new Date().toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' })}
             </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8">
        
        {/* SIDEBAR - INPUTS */}
        <div className="lg:col-span-3 space-y-6">
          
          {/* 1. SUPPORT & SETUP */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
             <h2 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">1. Support & Setup</h2>
             <div className="space-y-4">
                <div>
                   <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Support Level</label>
                   <select name="supportLevel" value={data.supportLevel} onChange={handleInputChange} className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white outline-none focus:border-blue-500">
                      {Object.keys(SUPPORT_OPTIONS).map(k => <option key={k} value={k}>{k}</option>)}
                   </select>
                </div>
                <div>
                   <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Your Hourly Rate ($)</label>
                   <input type="number" name="hourlyRate" value={data.hourlyRate} onChange={handleInputChange} step="0.01" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm font-mono text-white outline-none focus:border-blue-500" />
                </div>
             </div>
          </div>

          {/* 2. TIME LEFT */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
             <h2 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">2. Time Left in Plan</h2>
             
             {/* MODE SWITCHER */}
             <div className="flex bg-slate-800 rounded p-1 mb-4">
                <button 
                  onClick={() => handleInputChange({ target: { name: 'timeInputMode', value: 'dates' } } as any)} 
                  className={`flex-1 text-[10px] uppercase font-bold py-1.5 rounded transition-colors ${data.timeInputMode === 'dates' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Plan Dates
                </button>
                <button 
                  onClick={() => handleInputChange({ target: { name: 'timeInputMode', value: 'weeks' } } as any)}
                  className={`flex-1 text-[10px] uppercase font-bold py-1.5 rounded transition-colors ${data.timeInputMode === 'weeks' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Weeks Left
                </button>
             </div>

             <div className="space-y-4">
                {data.timeInputMode === 'dates' ? (
                   <>
                    <div>
                       <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Plan Start Date</label>
                       <input type="date" name="planStartDate" value={data.planStartDate} onChange={handleInputChange} className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white outline-none focus:border-blue-500" />
                    </div>
                    <div>
                       <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Plan End Date</label>
                       <input type="date" name="planEndDate" value={data.planEndDate} onChange={handleInputChange} className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white outline-none focus:border-blue-500" />
                    </div>
                    {results.daysRemaining <= 0 && (
                      <div className="text-xs text-red-400 font-bold text-center bg-red-900/20 p-2 rounded animate-pulse">
                          Error: Plan End Date must be in the future.
                      </div>
                    )}
                   </>
                ) : (
                   <div>
                      <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Weeks Remaining from Today</label>
                      <input type="number" name="manualWeeksRemaining" value={data.manualWeeksRemaining} onChange={handleInputChange} step="0.5" min="0.1" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-lg font-mono text-white outline-none focus:border-blue-500" />
                   </div>
                )}

                <div className="bg-blue-900/20 border border-blue-500/30 rounded p-2 text-center mt-2">
                   <div className="text-[10px] text-blue-300 uppercase font-bold">Time Calculation</div>
                   <div className="text-lg font-mono font-bold text-white">{results.daysRemaining} days</div>
                   <div className="text-xs text-blue-300">({results.weeksRemaining.toFixed(1)} weeks)</div>
                </div>
             </div>
          </div>

          {/* 3. FINANCIALS */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
             <h2 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">3. Financials (Portal Truth)</h2>
             <div className="space-y-4">
                <div>
                   <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Total Original Budget ($)</label>
                   <input type="number" name="totalBudget" value={data.totalBudget} onChange={handleInputChange} step="100" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm font-mono text-white outline-none focus:border-blue-500" />
                </div>
                <div>
                   <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Current Portal Balance ($)</label>
                   <input type="number" name="currentBalance" value={data.currentBalance} onChange={handleInputChange} step="50" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-sm font-mono text-emerald-400 font-bold outline-none focus:border-emerald-500" />
                </div>
             </div>
          </div>

          {/* 4. PLANNED BILLING */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
             <h2 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-4 border-b border-slate-800 pb-2">4. Planned Billing</h2>
             <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Planned Hours Per Week</label>
                <input type="number" name="hoursPerWeek" value={data.hoursPerWeek} onChange={handleInputChange} step="0.1" className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xl font-mono text-white font-bold outline-none focus:border-purple-500" />
             </div>
          </div>

          {/* DISCLAIMER TOGGLE */}
          <div className="border-t border-slate-800 pt-4">
             <button onClick={() => setShowDisclaimer(!showDisclaimer)} className="text-[10px] text-slate-500 hover:text-slate-300 w-full text-left flex justify-between">
                <span>⚠️ Disclaimer & Authorship</span>
                <span>{showDisclaimer ? '−' : '+'}</span>
             </button>
             {showDisclaimer && (
                <div className="mt-2 text-[10px] text-slate-500 leading-relaxed bg-slate-900 p-2 rounded border border-slate-800">
                    <p className="mb-2"><strong>NDIS Calculator Master Edition</strong><br/>Built by <strong>Chas Walker</strong> from <a href="https://www.xyston.com.au" target="_blank" className="text-blue-400 hover:underline">www.xyston.com.au</a></p>
                    <p className="mb-2">This tool is provided for <strong>informational and planning purposes only</strong>. All outputs rely entirely on the figures you enter and may not match NDIA decisions, plan manager records, or portal calculations.</p>
                    <p><strong>Use at your own risk.</strong> We accept <strong>no liability</strong> for any financial decisions, losses, or outcomes resulting from use of this calculator.</p>
                </div>
             )}
          </div>

        </div>

        {/* DASHBOARD - OUTPUT */}
        <div className="lg:col-span-9 space-y-6">
          
          {/* 1. BIG VISUAL STATUS */}
          <div className={`rounded-xl p-6 border-2 ${results.statusBg} text-center relative overflow-hidden transition-all duration-500`}>
             <h1 className={`text-3xl md:text-4xl font-black tracking-tight mb-3 ${results.status.includes("PLATINUM") ? 'text-emerald-400' : results.status.includes("VIABLE") ? 'text-green-400' : results.status.includes("TIGHT") ? 'text-yellow-400' : 'text-red-500'}`}>
                {results.status}
             </h1>
             <p className="text-lg md:text-xl text-white/90">
                You have <strong className="font-mono text-white border-b border-white/30">{results.runwayWeeks.toFixed(1)} weeks</strong> of funding for <strong className="font-mono text-white border-b border-white/30">{results.weeksRemaining.toFixed(1)} weeks</strong> of time.
             </p>
          </div>

          {/* 2. FINANCIAL SNAPSHOT */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
             <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span>💼</span> Financial Snapshot
             </h3>
             <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                <div>
                   <div className="text-[10px] text-slate-500 uppercase font-bold">Funds Available Now</div>
                   <div className="text-xl font-mono font-bold text-white">${data.currentBalance.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                   <div className="text-xs text-emerald-500/70 font-medium">Source: Portal</div>
                </div>
                <div>
                   <div className="text-[10px] text-slate-500 uppercase font-bold">Your Weekly Bill</div>
                   <div className="text-xl font-mono font-bold text-white">${results.weeklyCost.toFixed(2)}</div>
                   <div className="text-xs text-slate-400">{data.hoursPerWeek.toFixed(1)} hrs @ ${data.hourlyRate.toFixed(2)}</div>
                </div>
                <div>
                   <div className="text-[10px] text-slate-500 uppercase font-bold">Depletion Date</div>
                   <div className="text-xl font-mono font-bold text-white truncate">{results.depletionDateFormatted}</div>
                   <div className="text-xs text-slate-400">Plan ends {results.planEndDateFormatted}</div>
                </div>
                <div>
                   <div className="text-[10px] text-slate-500 uppercase font-bold">Outcome at Plan End</div>
                   <div className={`text-xl font-mono font-bold ${results.surplusShortfall >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {results.surplusShortfall >= 0 ? '+' : ''}${Math.abs(results.surplusShortfall).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                   </div>
                   <div className="text-xs text-slate-400">{results.surplusShortfall >= 0 ? 'Surplus' : 'Shortfall'}</div>
                </div>
             </div>
          </div>

          {/* 3. CHARTS ROW */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[300px]">
             
             {/* PIE */}
             <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider text-center mb-2">📊 Budget Usage</h4>
                <div className="flex-grow">
                   <PieChart spent={results.spent} available={data.currentBalance} />
                </div>
             </div>

             {/* TRAJECTORY */}
             <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider text-center mb-2">📉 The Trajectory</h4>
                <div className="flex-grow">
                   <TrajectoryChart 
                      data={results.burnDownData} 
                      planEndDate={results.planEndDateFormatted} 
                      statusColor={results.statusColor}
                   />
                </div>
             </div>
          </div>

          {/* 4. INSTANT ADVICE & AI */}
          <div className="space-y-4">
              
              {/* STATIC ADVICE (Always Visible) */}
              <div className={`rounded-xl p-6 border-l-4 shadow-lg ${
                  results.instantAdvice.type === 'danger' ? 'bg-red-900/10 border-red-500' :
                  results.instantAdvice.type === 'opportunity' ? 'bg-blue-900/10 border-blue-500' :
                  'bg-emerald-900/10 border-emerald-500'
              }`}>
                  <h3 className={`text-lg font-bold mb-3 ${
                      results.instantAdvice.type === 'danger' ? 'text-red-400' :
                      results.instantAdvice.type === 'opportunity' ? 'text-blue-400' :
                      'text-emerald-400'
                  }`}>
                      {results.instantAdvice.header}
                  </h3>
                  <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap markdown-prose" dangerouslySetInnerHTML={{ 
                     __html: results.instantAdvice.body
                        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
                  }} />
              </div>

              {/* AI EXPANDER */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <div className="p-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                          <span className="text-xl">🤖</span>
                          <h3 className="font-bold text-white">Ask for a Deep Dive</h3>
                      </div>
                      {!aiAnalysis && (
                          <button 
                             onClick={handleAskAI} 
                             disabled={loadingAi}
                             className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded border border-slate-700 transition-colors"
                          >
                             {loadingAi ? 'Analyzing...' : 'Generate Report'}
                          </button>
                      )}
                  </div>
                  
                  {aiAnalysis && (
                      <div className="p-6 bg-slate-950 text-sm text-slate-300 leading-relaxed animate-in fade-in duration-500 prose prose-invert max-w-none">
                          <div dangerouslySetInnerHTML={{ __html: aiAnalysis }} />
                      </div>
                  )}
              </div>

          </div>

          <div className="text-center text-[10px] text-slate-600 py-4">
             © 2025 NDIS Calculator Master Edition | Built by Chas Walker · Xyston.com.au
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
