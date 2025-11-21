
export type SupportLevel = "Level 2: Coordination of Supports" | "Level 3: Specialist Support Coordination";

export interface ClientData {
  supportLevel: SupportLevel;
  hourlyRate: number;
  timeInputMode: 'dates' | 'weeks';
  planStartDate: string; // ISO YYYY-MM-DD
  planEndDate: string;   // ISO YYYY-MM-DD
  manualWeeksRemaining: number;
  totalBudget: number;
  currentBalance: number; // Portal Truth
  hoursPerWeek: number;
}

export interface BurnDownPoint {
  date: string;
  balance: number;
}

export interface InstantAdvice {
  header: string;
  body: string;
  type: 'danger' | 'opportunity' | 'success';
}

export interface AnalysisResult {
  // Time
  daysRemaining: number;
  weeksRemaining: number;
  planStartDateFormatted: string;
  planEndDateFormatted: string;
  depletionDateFormatted: string;
  
  // Money
  spent: number;
  weeklyCost: number;
  runwayWeeks: number;
  requiredToFinish: number;
  surplusShortfall: number;
  bufferWeeks: number;
  breakEvenHours: number;
  
  // Status
  status: string;
  statusColor: string;
  statusBg: string; // Tailwind class
  
  // Advice
  instantAdvice: InstantAdvice;

  // Chart
  burnDownData: BurnDownPoint[];
}
