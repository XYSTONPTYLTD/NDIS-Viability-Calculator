export type SupportLevel = "Level 2: Coordination of Supports" | "Level 3: Specialist Support Coordination";

export interface ClientData {
  supportLevel: SupportLevel;
  hourlyRate: number;
  timeInputMode: 'dates' | 'weeks';
  planStartDate: string;
  planEndDate: string;
  manualWeeksRemaining: number;
  totalBudget: number;
  currentBalance: number;
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
  daysRemaining: number;
  weeksRemaining: number;
  planStartDateFormatted: string;
  planEndDateFormatted: string;
  depletionDateFormatted: string;
  spent: number;
  weeklyCost: number;
  runwayWeeks: number;
  requiredToFinish: number;
  surplusShortfall: number;
  bufferWeeks: number;
  breakEvenHours: number;
  status: string;
  statusColor: string; // Hex code for charts
  statusBg: string;    // Tailwind classes for banners
  statusColorText: string; // Tailwind classes for text
  instantAdvice: InstantAdvice;
  burnDownData: BurnDownPoint[];
}
