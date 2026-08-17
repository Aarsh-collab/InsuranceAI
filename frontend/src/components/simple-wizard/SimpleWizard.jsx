import { useMemo, useState } from "react";
import {
  EMPTY_ANSWERS,
  HOUSEHOLD_OPTIONS,
  PRIORITY_OPTIONS,
  SIMPLE_STEPS,
} from "./types";
import {
  buildPayload,
  formatCurrency,
  householdLabel,
  priorityLabel,
  validateCashFlow,
  validateHousehold,
  validatePriority,
  validateProtection,
} from "./validation";

function cn(...parts) {
  return parts.filter(Boolean).join(" ");
}

const INPUT_CLASS =
  "flex h-10 w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c4a35a]";

const BUTTON_VARIANTS = {
  primary:
    "bg-[#c4a35a] text-black hover:brightness-105 disabled:opacity-40 disabled:hover:brightness-100",
  outline:
    "border border-zinc-700 text-zinc-200 hover:border-zinc-500 disabled:opacity-40",
  ghost: "text-zinc-400 hover:text-zinc-100 disabled:opacity-40",
};

function Button({ variant = "primary", className, ...props }) {
  return (
    <button
      type="button"
      className={cn(
        "rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed",
        BUTTON_VARIANTS[variant],
        className
      )}
      {...props}
    />
  );
}

function parseOptionalNumber(raw) {
  if (raw.trim() === "") return "";
  const n = Number(raw);
  return Number.isFinite(n) ? n : "";
}

export function SimpleWizard({ onComplete, className }) {
  const [stepIndex, setStepIndex] = useState(0);
  const [answers, setAnswers] = useState(EMPTY_ANSWERS);
  const [errors, setErrors] = useState({});
  const [completedPayload, setCompletedPayload] = useState(null);

  const step = SIMPLE_STEPS[stepIndex];
  const isReview = step.id === "review";

  const preview = useMemo(() => {
    try {
      return buildPayload(answers);
    } catch {
      return null;
    }
  }, [answers]);

  const updateField = (key, value) => {
    setAnswers((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => {
      if (!prev[key]) return prev;
      const next = { ...prev };
      delete next[key];
      return next;
    });
  };

  const validateStep = (id) => {
    switch (id) {
      case "household":
        return validateHousehold(answers);
      case "cashflow":
        return validateCashFlow(answers);
      case "protection":
        return validateProtection(answers);
      case "priority":
        return validatePriority(answers);
      default:
        return {};
    }
  };

  const goNext = () => {
    if (!isReview) {
      const nextErrors = validateStep(step.id);
      if (Object.keys(nextErrors).length > 0) {
        setErrors(nextErrors);
        return;
      }
      setErrors({});
      setStepIndex((i) => Math.min(i + 1, SIMPLE_STEPS.length - 1));
      return;
    }

    const payload = buildPayload(answers);
    setCompletedPayload(payload);
    onComplete?.(payload);
  };

  const goBack = () => {
    setErrors({});
    setStepIndex((i) => Math.max(i - 1, 0));
  };

  const reset = () => {
    setAnswers(EMPTY_ANSWERS);
    setErrors({});
    setCompletedPayload(null);
    setStepIndex(0);
  };

  if (completedPayload) {
    return (
      <div
        className={cn(
          "w-full max-w-xl rounded-lg border border-zinc-800 bg-zinc-950 p-6",
          className
        )}
      >
        <h2 className="text-lg font-semibold text-zinc-100">Intake ready</h2>
        <p className="mt-1.5 text-sm leading-relaxed text-zinc-400">
          Preliminary context only — not a quote or advice. This payload can be
          handed to InsuranceAI later.
        </p>

        <dl className="mt-6 space-y-3 text-sm">
          <SummaryRow
            label="Monthly cash flow"
            value={formatCurrency(completedPayload.derived.monthlyCashFlow)}
          />
          <SummaryRow
            label="Rule-of-thumb coverage need"
            value={formatCurrency(completedPayload.derived.estimatedCoverageNeed)}
          />
          <SummaryRow
            label="Coverage gap"
            value={formatCurrency(completedPayload.derived.coverageGap)}
          />
          <SummaryRow
            label="Top priority"
            value={priorityLabel(completedPayload.answers.topPriority)}
          />
        </dl>

        <pre className="mt-4 max-h-48 overflow-auto rounded-md border border-zinc-800 bg-zinc-900 p-3 text-xs text-zinc-400">
          {JSON.stringify(completedPayload, null, 2)}
        </pre>

        <div className="mt-6">
          <Button variant="outline" onClick={reset}>
            Start over
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "w-full max-w-xl rounded-lg border border-zinc-800 bg-zinc-950 p-6",
        className
      )}
    >
      <p className="text-xs font-medium uppercase tracking-wider text-[#c4a35a]">
        Step {stepIndex + 1} of {SIMPLE_STEPS.length}
      </p>
      <h2 className="mt-1 text-lg font-semibold text-zinc-100">{step.title}</h2>
      <p className="mt-1.5 text-sm leading-relaxed text-zinc-400">
        {step.description}
      </p>
      <div className="flex gap-1 pt-3">
        {SIMPLE_STEPS.map((s, i) => (
          <div
            key={s.id}
            className={cn(
              "h-1 flex-1 rounded-full",
              i <= stepIndex ? "bg-[#c4a35a]" : "bg-zinc-800"
            )}
            aria-hidden
          />
        ))}
      </div>

      <div className="mt-6">
        {step.id === "household" && (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field id="age" label="Age" error={errors.age}>
              <input
                id="age"
                type="number"
                min={18}
                max={100}
                inputMode="numeric"
                placeholder="30"
                className={INPUT_CLASS}
                value={answers.age}
                onChange={(e) =>
                  updateField("age", parseOptionalNumber(e.target.value))
                }
              />
            </Field>
            <Field id="state" label="State" error={errors.state}>
              <input
                id="state"
                placeholder="WA"
                className={INPUT_CLASS}
                value={answers.state}
                onChange={(e) => updateField("state", e.target.value)}
              />
            </Field>
            <Field
              id="householdStatus"
              label="Household status"
              error={errors.householdStatus}
              className="sm:col-span-2"
            >
              <select
                id="householdStatus"
                className={INPUT_CLASS}
                value={answers.householdStatus}
                onChange={(e) => updateField("householdStatus", e.target.value)}
              >
                <option value="">Select…</option>
                {HOUSEHOLD_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </Field>
            <Field
              id="dependentsCount"
              label="Dependents"
              error={errors.dependentsCount}
              className="sm:col-span-2"
            >
              <input
                id="dependentsCount"
                type="number"
                min={0}
                inputMode="numeric"
                placeholder="0"
                className={INPUT_CLASS}
                value={answers.dependentsCount}
                onChange={(e) =>
                  updateField(
                    "dependentsCount",
                    parseOptionalNumber(e.target.value)
                  )
                }
              />
            </Field>
          </div>
        )}

        {step.id === "cashflow" && (
          <div className="grid gap-4">
            <Field
              id="monthlyIncome"
              label="Monthly income ($)"
              error={errors.monthlyIncome}
            >
              <input
                id="monthlyIncome"
                type="number"
                min={0}
                inputMode="decimal"
                placeholder="6000"
                className={INPUT_CLASS}
                value={answers.monthlyIncome}
                onChange={(e) =>
                  updateField(
                    "monthlyIncome",
                    parseOptionalNumber(e.target.value)
                  )
                }
              />
            </Field>
            <Field
              id="monthlySpending"
              label="Monthly spending, excluding debt ($)"
              error={errors.monthlySpending}
            >
              <input
                id="monthlySpending"
                type="number"
                min={0}
                inputMode="decimal"
                placeholder="3500"
                className={INPUT_CLASS}
                value={answers.monthlySpending}
                onChange={(e) =>
                  updateField(
                    "monthlySpending",
                    parseOptionalNumber(e.target.value)
                  )
                }
              />
            </Field>
            <Field
              id="monthlyDebtPayments"
              label="Monthly debt payments ($)"
              error={errors.monthlyDebtPayments}
            >
              <input
                id="monthlyDebtPayments"
                type="number"
                min={0}
                inputMode="decimal"
                placeholder="500"
                className={INPUT_CLASS}
                value={answers.monthlyDebtPayments}
                onChange={(e) =>
                  updateField(
                    "monthlyDebtPayments",
                    parseOptionalNumber(e.target.value)
                  )
                }
              />
            </Field>
          </div>
        )}

        {step.id === "protection" && (
          <div className="grid gap-4">
            <Field
              id="liquidSavings"
              label="Liquid savings / emergency fund ($)"
              error={errors.liquidSavings}
            >
              <input
                id="liquidSavings"
                type="number"
                min={0}
                inputMode="decimal"
                placeholder="10000"
                className={INPUT_CLASS}
                value={answers.liquidSavings}
                onChange={(e) =>
                  updateField(
                    "liquidSavings",
                    parseOptionalNumber(e.target.value)
                  )
                }
              />
            </Field>
            <Field
              id="currentLifeCoverage"
              label="Current life insurance coverage ($)"
              error={errors.currentLifeCoverage}
            >
              <input
                id="currentLifeCoverage"
                type="number"
                min={0}
                inputMode="decimal"
                placeholder="0"
                className={INPUT_CLASS}
                value={answers.currentLifeCoverage}
                onChange={(e) =>
                  updateField(
                    "currentLifeCoverage",
                    parseOptionalNumber(e.target.value)
                  )
                }
              />
            </Field>
          </div>
        )}

        {step.id === "priority" && (
          <Field
            id="topPriority"
            label="Top priority right now"
            error={errors.topPriority}
          >
            <div className="grid gap-2">
              {PRIORITY_OPTIONS.map((o) => (
                <button
                  key={o.value}
                  type="button"
                  onClick={() => updateField("topPriority", o.value)}
                  className={cn(
                    "rounded-md border px-3 py-3 text-left text-sm transition-colors",
                    answers.topPriority === o.value
                      ? "border-[#c4a35a] bg-[#c4a35a]/10 text-zinc-100"
                      : "border-zinc-700 bg-zinc-900 text-zinc-300 hover:border-zinc-500"
                  )}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </Field>
        )}

        {step.id === "review" && preview && (
          <div className="space-y-4 text-sm">
            <p className="rounded-md border border-zinc-800 bg-zinc-900/60 px-3 py-2 text-zinc-400">
              Informational only. Not a quote, underwriting decision, or
              financial advice.
            </p>
            <dl className="space-y-3">
              <SummaryRow
                label="Profile"
                value={`${preview.answers.age}, ${preview.answers.state}, ${householdLabel(preview.answers.householdStatus)}, ${preview.answers.dependentsCount} dependent(s)`}
              />
              <SummaryRow
                label="Monthly income"
                value={formatCurrency(preview.answers.monthlyIncome)}
              />
              <SummaryRow
                label="Monthly cash flow"
                value={formatCurrency(preview.derived.monthlyCashFlow)}
              />
              <SummaryRow
                label="Liquid savings"
                value={formatCurrency(preview.answers.liquidSavings)}
              />
              <SummaryRow
                label="Current life coverage"
                value={formatCurrency(preview.answers.currentLifeCoverage)}
              />
              <SummaryRow
                label="Rule-of-thumb coverage need"
                value={formatCurrency(preview.derived.estimatedCoverageNeed)}
              />
              <SummaryRow
                label="Coverage gap"
                value={formatCurrency(preview.derived.coverageGap)}
              />
              <SummaryRow
                label="Top priority"
                value={priorityLabel(preview.answers.topPriority)}
              />
            </dl>
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <Button variant="ghost" onClick={goBack} disabled={stepIndex === 0}>
          Back
        </Button>
        <div className="flex gap-2">
          <Button variant="outline" onClick={reset}>
            Start over
          </Button>
          <Button onClick={goNext}>
            {isReview ? "Submit intake" : "Continue"}
          </Button>
        </div>
      </div>
    </div>
  );
}

function Field({ id, label, error, className, children }) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <label htmlFor={id} className="text-sm text-zinc-300">
        {label}
      </label>
      {children}
      {error ? <p className="text-xs text-red-400">{error}</p> : null}
    </div>
  );
}

function SummaryRow({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-zinc-800/80 pb-2">
      <dt className="text-zinc-400">{label}</dt>
      <dd className="text-right font-medium text-zinc-100">{value}</dd>
    </div>
  );
}
