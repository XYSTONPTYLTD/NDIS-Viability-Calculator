
export const DEFAULTS = {
  HOURLY_RATE: 100.14,
  TOTAL_BUDGET: 18000.00,
  CURRENT_BALANCE: 14500.00,
  HOURS_PER_WEEK: 1.5,
  TIME_INPUT_MODE: 'dates' as const,
  MANUAL_WEEKS: 40,
  // Dates calculated dynamically in App.tsx
};

export const SUPPORT_OPTIONS = {
  "Level 2: Coordination of Supports": 100.14,
  "Level 3: Specialist Support Coordination": 190.41
};

export const COLORS = {
  PLATINUM: '#00cc66',
  VIABLE: '#66ff66',
  TIGHT: '#ffff00',
  NON_VIABLE: '#ff4444',
  
  PIE_SPENT: '#ffaaaa',
  PIE_AVAILABLE: '#aaffaa',
  
  BG_DARK: '#0f172a',
};
