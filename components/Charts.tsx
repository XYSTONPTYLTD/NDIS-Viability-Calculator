
import React from 'react';
import { BurnDownPoint } from '../types';
import { COLORS } from '../constants';

interface PieChartProps {
  spent: number;
  available: number;
}

export const PieChart: React.FC<PieChartProps> = ({ spent, available }) => {
  const total = Math.max(0, spent) + available;
  if (total <= 0) return null;
  
  const spentPercent = (Math.max(0, spent) / total);
  
  // Calculate donut segment
  // We want a simple 2-slice pie
  // Coordinates for SVG arc
  const getCoords = (percent: number) => {
    const x = Math.cos(2 * Math.PI * percent);
    const y = Math.sin(2 * Math.PI * percent);
    return [x, y];
  };

  const [startX, startY] = getCoords(0); // Start at right (0 rad) or top? transform -90 handles top
  const [endX, endY] = getCoords(spentPercent);
  const largeArcFlag = spentPercent > 0.5 ? 1 : 0;

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="relative w-40 h-40">
        <svg viewBox="-1 -1 2 2" className="w-full h-full transform -rotate-90">
          {/* Background Circle (Available) */}
          <circle cx="0" cy="0" r="1" fill={COLORS.PIE_AVAILABLE} />
          
          {/* Spent Slice */}
          {spentPercent > 0 && spentPercent < 1 && (
            <path 
              d={`M 0 0 L ${startX} ${startY} A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY} Z`}
              fill={COLORS.PIE_SPENT}
            />
          )}
          {spentPercent >= 1 && <circle cx="0" cy="0" r="1" fill={COLORS.PIE_SPENT} />}
          
          {/* Center Hole for Donut */}
          <circle cx="0" cy="0" r="0.5" fill="#1e293b" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
           <span className="text-lg font-bold">${(available/1000).toFixed(1)}k</span>
           <span className="text-[10px] text-slate-400 uppercase">Left</span>
        </div>
      </div>
      <div className="flex gap-4 mt-4 text-xs">
         <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full" style={{background: COLORS.PIE_SPENT}}></div>
            <span className="text-slate-300">Spent</span>
         </div>
         <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full" style={{background: COLORS.PIE_AVAILABLE}}></div>
            <span className="text-slate-300">Available</span>
         </div>
      </div>
    </div>
  );
};

interface TrajectoryChartProps {
  data: BurnDownPoint[];
  planEndDate: string;
  statusColor: string;
}

export const TrajectoryChart: React.FC<TrajectoryChartProps> = ({ data, planEndDate, statusColor }) => {
  if (!data || data.length === 0) return null;

  const width = 600;
  const height = 300;
  const padding = 40;

  const maxBalance = Math.max(...data.map(d => d.balance)) * 1.1;
  
  // Time scale
  const startDate = new Date(data[0].date).getTime();
  const endDate = new Date(data[data.length - 1].date).getTime();
  const totalTime = endDate - startDate;

  const xScale = (dateStr: string) => {
     const t = new Date(dateStr).getTime();
     return padding + ((t - startDate) / totalTime) * (width - padding * 2);
  };

  const yScale = (bal: number) => {
     return height - padding - (bal / maxBalance) * (height - padding * 2);
  };

  // Plan End Line X
  const planEndX = xScale(planEndDate);

  // Generate Path
  const pathD = data.map((pt, i) => 
     `${i === 0 ? 'M' : 'L'} ${xScale(pt.date)} ${yScale(pt.balance)}`
  ).join(' ');

  return (
    <div className="w-full h-full min-h-[250px]">
       <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
          {/* Grid Lines */}
          {[0, 0.5, 1].map(t => {
             const val = maxBalance * t;
             const y = yScale(val);
             return (
                <line key={t} x1={padding} y1={y} x2={width-padding} y2={y} stroke="#334155" strokeDasharray="4" />
             );
          })}
          
          {/* Zero Line */}
          <line x1={padding} y1={yScale(0)} x2={width-padding} y2={yScale(0)} stroke="#64748b" />

          {/* Plan End Vertical Line */}
          <line 
            x1={planEndX} y1={padding} 
            x2={planEndX} y2={height-padding} 
            stroke="#cbd5e1" strokeDasharray="4" strokeWidth="2" 
          />
          <text x={planEndX} y={padding - 10} textAnchor="middle" className="text-xs fill-slate-300 font-bold">
             PLAN END
          </text>

          {/* Trajectory Line */}
          <path d={pathD} fill="none" stroke={statusColor} strokeWidth="3" />

          {/* Axes Labels */}
          <text x={padding} y={yScale(maxBalance)} textAnchor="end" dominantBaseline="middle" className="text-[10px] fill-slate-500 mr-2">${(maxBalance/1000).toFixed(0)}k</text>
          <text x={padding} y={yScale(0)} textAnchor="end" dominantBaseline="middle" className="text-[10px] fill-slate-500 mr-2">$0</text>
          
          {/* X Axis Date Labels */}
          <text x={padding} y={height-10} textAnchor="middle" className="text-[10px] fill-slate-500">Today</text>
          <text x={width-padding} y={height-10} textAnchor="middle" className="text-[10px] fill-slate-500">Future</text>
       </svg>
    </div>
  );
};
