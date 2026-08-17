export const EMPTY_ANSWERS = {
  age: "",
  state: "",
  householdStatus: "",
  dependentsCount: "",
  monthlyIncome: "",
  monthlySpending: "",
  monthlyDebtPayments: "",
  liquidSavings: "",
  currentLifeCoverage: "",
  topPriority: "",
};

export const HOUSEHOLD_OPTIONS = [
  { value: "single", label: "Single" },
  { value: "married", label: "Married" },
  { value: "partnered", label: "Partnered" },
];

export const PRIORITY_OPTIONS = [
  { value: "life_protection", label: "Life protection / income replacement" },
  { value: "emergency_fund", label: "Emergency fund" },
  { value: "debt_paydown", label: "Debt paydown" },
  { value: "retirement", label: "Retirement savings" },
  { value: "other", label: "Something else" },
];

export const SIMPLE_STEPS = [
  {
    id: "household",
    title: "Household",
    description: "Basic profile context for a life-insurance conversation.",
  },
  {
    id: "cashflow",
    title: "Cash flow",
    description: "Monthly money in and out — keeps estimates grounded.",
  },
  {
    id: "protection",
    title: "Protection",
    description: "Savings cushion and any coverage you already have.",
  },
  {
    id: "priority",
    title: "Priority",
    description: "What matters most so the assistant can stay focused.",
  },
  {
    id: "review",
    title: "Review",
    description: "Confirm the handoff summary for InsuranceAI.",
  },
];
