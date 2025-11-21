
import { ClientData, AnalysisResult, BurnDownPoint, InstantAdvice } from '../types';
import { COLORS } from '../constants';

export const calculateViability = (data: ClientData): AnalysisResult => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  let startDate = new Date(data.planStartDate);
  let endDate = new Date(data.planEndDate);
  let daysRemaining = 0;
  let weeksRemaining = 0;

  // 1. Time Calculations (Fail-Safe logic based on mode)
  const msPerDay = 1000 * 60 * 60 * 24;

  if (data.timeInputMode === 'weeks') {
    // If manual weeks entered, calculate End Date from it
    weeksRemaining = data.manualWeeksRemaining;
    daysRemaining = Math.round(weeksRemaining * 7);
    
    // Set End Date based on weeks
    const targetDate = new Date(today);
    targetDate.setDate(targetDate.getDate() + daysRemaining);
    endDate = targetDate;
    
    // Start date is informational only in this mode
  } else {
    // 'dates' mode: Strict calc from plan end date
    endDate.setHours(0, 0, 0, 0);
    daysRemaining = Math.ceil((endDate.getTime() - today.getTime()) / msPerDay);
    weeksRemaining = daysRemaining > 0 ? daysRemaining / 7 : 0;
  }

  // 2. Financials
  const spent = Math.max(0, data.totalBudget - data.currentBalance);
  const weeklyCost = data.hoursPerWeek * data.hourlyRate;
  
  // 3. Runway
  const runwayWeeks = weeklyCost > 0 ? data.currentBalance / weeklyCost : 999;
  const runwayDays = Math.floor(runwayWeeks * 7);
  
  const depletionDate = new Date(today);
  depletionDate.setDate(depletionDate.getDate() + runwayDays);

  // 4. The Gap
  const requiredToFinish = weeklyCost * weeksRemaining;
  const surplusShortfall = data.currentBalance - requiredToFinish;
  const bufferWeeks = runwayWeeks - weeksRemaining;

  // 5. Status Logic (Fail-Safe Tiers)
  let status = "";
  let statusColor = "";
  let statusBg = "";

  if (runwayWeeks >= weeksRemaining * 1.2) {
    status = "🟢 PLATINUM CLIENT (Safe Surplus)";
    statusColor = COLORS.PLATINUM;
    statusBg = "bg-emerald-900/30 border-emerald-500";
  } else if (runwayWeeks >= weeksRemaining) {
    status = "🟢 VIABLE (On Track)";
    statusColor = COLORS.VIABLE;
    statusBg = "bg-green-900/30 border-green-500";
  } else if (runwayWeeks >= Math.max(0, weeksRemaining - 2)) {
    status = "🟡 TIGHT (Monitor Closely)";
    statusColor = COLORS.TIGHT;
    statusBg = "bg-yellow-900/30 border-yellow-500";
  } else {
    status = "🔴 NON-VIABLE (Immediate Action Req)";
    statusColor = COLORS.NON_VIABLE;
    statusBg = "bg-red-900/30 border-red-500";
  }

  // 6. Break Even
  const breakEvenHours = (weeksRemaining > 0 && data.hourlyRate > 0) 
    ? (data.currentBalance / (weeksRemaining * data.hourlyRate))
    : 0;

  // 7. Instant Advice (Rule-Based matched to Python script)
  let instantAdvice: InstantAdvice;
  const planEndDateStr = endDate.toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });
  const depletionDateStr = depletionDate.toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });
  
  const breakEvenText = breakEvenHours > 0 ? `**${breakEvenHours.toFixed(2)} hours/week**` : "**N/A**";

  if (surplusShortfall < -500) {
    instantAdvice = {
      header: "⚠️ DANGER: You are burning too hot.",
      type: 'danger',
      body: `At **${data.hoursPerWeek.toFixed(2)} hours/week**, this participant will run out of money on **${depletionDateStr}** — which is **${Math.abs(bufferWeeks).toFixed(1)} weeks earlier** than the plan end date.\n\n**Corrective Action:**\n1. You must reduce billing to ${breakEvenText} to just break even by **${planEndDateStr}**.\n2. If the client genuinely needs this level of support, you should prepare evidence and consider a review (e.g. s48 or Change of Circumstances).`
    };
  } else if (surplusShortfall > 2000) {
    instantAdvice = {
      header: "💎 OPPORTUNITY: You are under-servicing.",
      type: 'opportunity',
      body: `You have a projected surplus of **$${surplusShortfall.toLocaleString('en-AU', {minimumFractionDigits: 2, maximumFractionDigits: 2})}**. If you continue at this rate, you will return money to the NDIA at **${planEndDateStr}**.\n\n**Strategy:**\n* You can safely increase support up to around ${breakEvenText} if clinically justified.\n* Consider using this headroom for extra coordination, reports, provider meetings, or capacity building that genuinely benefits the participant.`
    };
  } else {
    instantAdvice = {
      header: "✅ ON TRACK: Balanced use of funding.",
      type: 'success',
      body: `At your current plan of **${data.hoursPerWeek.toFixed(2)} hours/week**, you are on track to finish this plan with approximately **$${surplusShortfall.toLocaleString('en-AU', {minimumFractionDigits: 2, maximumFractionDigits: 2})}** remaining.\n\nKeep monitoring the portal balance and adjust hours slightly if there are major changes in the participant's needs.`
    };
  }

  // 8. Chart Data (Trajectory)
  // Generate points for weeksRemaining + 4 extra weeks
  const burnDownData: BurnDownPoint[] = [];
  const weeksToChart = Math.ceil(weeksRemaining) + 4;
  
  for (let w = 0; w <= weeksToChart; w++) {
    const futureDate = new Date(today);
    futureDate.setDate(futureDate.getDate() + (w * 7));
    const balance = Math.max(0, data.currentBalance - (w * weeklyCost));
    
    burnDownData.push({
      date: futureDate.toISOString(),
      balance: balance
    });
  }

  return {
    daysRemaining,
    weeksRemaining,
    planStartDateFormatted: startDate.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' }),
    planEndDateFormatted: endDate.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' }),
    depletionDateFormatted: depletionDate.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' }),
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
    instantAdvice,
    burnDownData
  };
};
