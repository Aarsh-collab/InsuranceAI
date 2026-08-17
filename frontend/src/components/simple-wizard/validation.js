import { HOUSEHOLD_OPTIONS, PRIORITY_OPTIONS } from "./types";

function isNonNegativeNumber(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}

function isPositiveInt(value) {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

export function validateHousehold(answers) {
  const errors = {};
  if (!isPositiveInt(answers.age) || answers.age < 18 || answers.age > 100) {
    errors.age = "Enter an age between 18 and 100.";
  }
  if (!answers.state.trim()) {
    errors.state = "Enter your state (e.g. WA).";
  }
  if (!answers.householdStatus) {
    errors.householdStatus = "Select a household status.";
  }
  if (!isPositiveInt(answers.dependentsCount)) {
    errors.dependentsCount = "Enter dependents as 0 or more.";
  }
  return errors;
}

export function validateCashFlow(answers) {
  const errors = {};
  if (!isNonNegativeNumber(answers.monthlyIncome)) {
    errors.monthlyIncome = "Enter monthly income.";
  }
  if (!isNonNegativeNumber(answers.monthlySpending)) {
    errors.monthlySpending = "Enter monthly spending.";
  }
  if (!isNonNegativeNumber(answers.monthlyDebtPayments)) {
    errors.monthlyDebtPayments = "Enter monthly debt payments (0 is fine).";
  }
  return errors;
}

export function validateProtection(answers) {
  const errors = {};
  if (!isNonNegativeNumber(answers.liquidSavings)) {
    errors.liquidSavings = "Enter liquid savings (0 is fine).";
  }
  if (!isNonNegativeNumber(answers.currentLifeCoverage)) {
    errors.currentLifeCoverage = "Enter current life coverage (0 is fine).";
  }
  return errors;
}

export function validatePriority(answers) {
  const errors = {};
  if (!answers.topPriority) {
    errors.topPriority = "Choose a top priority.";
  }
  return errors;
}

export function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function householdLabel(value) {
  return HOUSEHOLD_OPTIONS.find((o) => o.value === value)?.label ?? value;
}

export function priorityLabel(value) {
  return PRIORITY_OPTIONS.find((o) => o.value === value)?.label ?? value;
}

/** Rough rule-of-thumb: ~10x annual income for income-replacement context. */
export function estimateCoverageNeed(monthlyIncome) {
  return Math.round(monthlyIncome * 12 * 10);
}

export function buildPayload(answers) {
  const monthlyIncome = Number(answers.monthlyIncome) || 0;
  const monthlySpending = Number(answers.monthlySpending) || 0;
  const monthlyDebtPayments = Number(answers.monthlyDebtPayments) || 0;
  const currentLifeCoverage = Number(answers.currentLifeCoverage) || 0;
  const estimatedCoverageNeed = estimateCoverageNeed(monthlyIncome);
  const monthlyCashFlow = monthlyIncome - monthlySpending - monthlyDebtPayments;

  return {
    version: 1,
    source: "simple-wizard",
    completedAt: new Date().toISOString(),
    answers: {
      age: Number(answers.age),
      state: answers.state.trim(),
      householdStatus: answers.householdStatus,
      dependentsCount: Number(answers.dependentsCount),
      monthlyIncome,
      monthlySpending,
      monthlyDebtPayments,
      liquidSavings: Number(answers.liquidSavings) || 0,
      currentLifeCoverage,
      topPriority: answers.topPriority,
    },
    derived: {
      monthlyCashFlow,
      estimatedCoverageNeed,
      coverageGap: Math.max(0, estimatedCoverageNeed - currentLifeCoverage),
    },
  };
}
