import React from 'react';
import { BurnDownPoint } from '../types';
import { COLORS } from '../constants';

export const PieChart = ({ spent, available }: { spent: number, available: number }) => {
  const total = spent + available;
  const spentPct = total > 0 ? (spent / total) * 100 : 0;
  
  return (
    <div className="flex flex-col items-center justify-center h-full">
       <div 
         className="w-32 h-32 rounded-full mb-4"
         style={{ background: `conic-gradient(${COLORS.PIE_SPENT} ${spentPct}%, ${COLORS.PIE_AVAILABLE} 0)` }}
       />
       <div className="flex gap-4 text-[10px] uppercase font-bold">
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full" style={{background: COLORS.PIE_SPENT}}></div> Used</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full" style={{background: COLORS.PIE_AVAILABLE}}></div> Available</div>
       </div>
    </div>
  );
};

export const TrajectoryChart = ({ data, planEndDate, statusColor }: { data: BurnDownPoint[], planEndDate: string, statusColor: string }) => {
  if (!data || !data.length) return null;
  const maxVal = Math.max(...data.map(d => d.balance));
  const height = 200;
  
  const points = data.map((d, i) => {
     const x = (i / (data.length - 1)) * 100;
     const y = height - ((d.balance / maxVal) * height);
     return `${x},${y}`;
  }).join(' ');

  return (
    <div className="relative w-full h-[200px] border-l border-b border-slate-700">
       <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox={`0 0 100 ${height}`}>
          <polyline points={points} fill="none" stroke={statusColor} strokeWidth="2" vectorEffect="non-scaling-stroke" />
       </svg>
       <div className="absolute bottom-0 right-0 text-[9px] text-slate-500 translate-y-4">Future</div>
       <div className="absolute bottom-0 left-0 text-[9px] text-slate-500 translate-y-4">Today</div>
       <div className="absolute top-2 right-2 text-xs text-slate-600 font-mono">Plan End: {planEndDate}</div>
    </div>
  );
};
