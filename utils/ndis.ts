import { ClientData, AnalysisResult, BurnDownPoint, InstantAdvice } from '../types';
import { COLORS } from '../constants';

export const calculateViability = (data: ClientData): AnalysisResult => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  let startDate = new Date(data.planStartDate);
  let endDate = new Date(data.planEndDate);
  let daysRemaining = 0;
  let weeksRemaining = 0;

  // 1. Time Calculations
  const msPerDay = 1000 * 60 * 60 * 24;
  if (data.timeInputMode === 'weeks') {
    weeksRemaining = data.manualWeeksRemaining;
    daysRemaining = Math.round(weeksRemaining * 7);
    const targetDate = new Date(today);
    targetDate.setDate(targetDate.getDate() + daysRemaining);
    endDate = targetDate;
  } else {
    endDate.setHours(0, 0, 0, 0);
    daysRemaining = Math.ceil((endDate.getTime() - today.getTime()) / msPerDay);
    weeksRemaining = Math.max(0, daysRemaining / 7);
  }

  // 2. Financials
  const spent = Math.max(0, data.totalBudget - data.currentBalance);
  const weeklyCost = data.hoursPerWeek * data.hourlyRate;
  
  // 3. Runway
  const runwayWeeks = weeklyCost > 0 ? data.currentBalance / weeklyCost : 999;
  const runwayDays = Math.floor(runwayWeeks * 7);
  
  const depletionDate = new Date(today);
  depletionDate.setDate(depletionDate.getDate() + runwayDays);

  // 4. Gap Analysis
  const requiredToFinish = weeklyCost * weeksRemaining;
  const surplusShortfall = data.currentBalance - requiredToFinish;
  const bufferWeeks = runwayWeeks - weeksRemaining;

  // 5. Status Logic
  let status = "";
  let statusColor = "";
  let statusBg = "";
  let statusColorText = "";

  if (runwayWeeks >= weeksRemaining * 1.2) {
    status = "PLATINUM CLIENT";
    statusColor = COLORS.PLATINUM;
    statusBg = "bg-emerald-900/30 border-emerald-500";
    statusColorText = "text-emerald-400";
  } else if (runwayWeeks >= weeksRemaining) {
    status = "VIABLE (On Track)";
    statusColor = COLORS.VIABLE;
    statusBg = "bg-green-900/30 border-green-500";
    statusColorText = "text-green-400";
  } else if (runwayWeeks >= Math.max(0, weeksRemaining - 2)) {
    status = "TIGHT (Monitor)";
    statusColor = COLORS.TIGHT;
    statusBg = "bg-yellow-900/30 border-yellow-500";
    statusColorText = "text-yellow-400";
  } else {
    status = "NON-VIABLE";
    statusColor = COLORS.NON_VIABLE;
    statusBg = "bg-red-900/30 border-red-500";
    statusColorText = "text-red-500";
  }

  // 6. Break Even
  const breakEvenHours = (weeksRemaining > 0 && data.hourlyRate > 0) 
    ? (data.currentBalance / (weeksRemaining * data.hourlyRate))
    : 0;

  // 7. Instant Advice
  let instantAdvice: InstantAdvice;
  const depletionDateStr = depletionDate.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
  const breakEvenText = breakEvenHours > 0 ? `**${breakEvenHours.toFixed(2)} hours/week**` : "**N/A**";

  if (surplusShortfall < -500) {
    instantAdvice = {
      header: "⚠️ DANGER: Burning too hot.",
      type: 'danger',
      body: `You will run out of money on **${depletionDateStr}** (${Math.abs(bufferWeeks).toFixed(1)} weeks early).\n\n**Action:** Reduce to ${breakEvenText} to break even.`
    };
  } else if (surplusShortfall > 2000) {
    instantAdvice = {
      header: "💎 OPPORTUNITY: Underservicing.",
      type: 'opportunity',
      body: `Projected surplus of **$${surplusShortfall.toLocaleString()}**. You can safely increase support to ${breakEvenText}.`
    };
  } else {
    instantAdvice = {
      header: "✅ ON TRACK: Balanced.",
      type: 'success',
      body: `You are perfectly aligned with the plan duration. Maintain current schedule.`
    };
  }

  // 8. Chart Data
  const burnDownData: BurnDownPoint[] = [];
  const weeksToChart = Math.ceil(weeksRemaining) + 4;
  for (let w = 0; w <= weeksToChart; w++) {
    const futureDate = new Date(today);
    futureDate.setDate(futureDate.getDate() + (w * 7));
    burnDownData.push({
      date: futureDate.toISOString(),
      balance: Math.max(0, data.currentBalance - (w * weeklyCost))
    });
  }

  return {
    daysRemaining,
    weeksRemaining,
    planStartDateFormatted: startDate.toLocaleDateString('en-AU'),
    planEndDateFormatted: endDate.toLocaleDateString('en-AU'),
    depletionDateFormatted: depletionDate.toLocaleDateString('en-AU'),
    spent,
    weeklyCost,
    runwayWeeks,
    requiredToFinish,
    surplusShortfall,
    bufferWeeks,
    breakEvenHours,
    status,
    statusColor,
    statusBg,
    statusColorText,
    instantAdvice,
    burnDownData
  };
};
