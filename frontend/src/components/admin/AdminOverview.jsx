import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchLeads } from "../../services/adminApi";
import StatusBadge from "./StatusBadge";

function AdminOverview() {
  const [leads, setLeads] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeads()
      .then(setLeads)
      .catch((err) => {
        if (err.status === 401) {
          navigate("/admin/login", { replace: true });
          return;
        }
        setError(err.message);
      });
  }, [navigate]);

  const stats = useMemo(() => buildStats(leads), [leads]);
  const recentQuotes = useMemo(
    () => leads.filter((lead) => lead.ml_quote != null).slice(0, 5),
    [leads]
  );
  const reviewQueue = useMemo(
    () =>
      leads
        .filter((lead) => lead.lead_quality?.score !== "low" && (!lead.completed || lead.meeting_requested))
        .slice(0, 5),
    [leads]
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Dashboard"
        title="Underwriting Operations"
        description="Live operational view of captured leads, premium estimates, policy uploads, and application review status."
      />

      {error && <ErrorPanel message={error} />}

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total leads" value={stats.total} detail="All captured sessions" />
        <MetricCard label="Pending applications" value={stats.pendingApplications} detail="Incomplete intake records" />
        <MetricCard label="Premium estimates" value={stats.completedQuotes} detail="Quotes generated" />
        <MetricCard label="Policy uploads" value={stats.policyUploads} detail="DEC pages received" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel title="Lead Quality Overview" subtitle="Rule-based quality from contact, quote, and meeting signals.">
          <BarRows
            total={Math.max(stats.total, 1)}
            items={[
              { label: "High quality", value: stats.quality.high, tone: "bg-emerald-300" },
              { label: "Medium quality", value: stats.quality.medium, tone: "bg-[#d7ad55]" },
              { label: "Low quality", value: stats.quality.low, tone: "bg-red-300" },
            ]}
          />
        </Panel>

        <Panel title="Application Review States" subtitle="Derived from existing quote completion and handoff data.">
          <BarRows
            total={Math.max(stats.total, 1)}
            items={[
              { label: "Started", value: stats.total, tone: "bg-white/45" },
              { label: "Quote generated", value: stats.completedQuotes, tone: "bg-[#d7ad55]" },
              { label: "Broker follow-up", value: stats.meetingRequests, tone: "bg-emerald-300" },
            ]}
          />
        </Panel>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Panel title="Lead Review Queue" subtitle="Qualified or in-progress leads needing broker review.">
          <LeadList leads={reviewQueue} emptyText="No leads currently require review." />
        </Panel>

        <Panel title="Recent Premium Estimates" subtitle="Latest sessions with model-generated monthly estimates.">
          <LeadList leads={recentQuotes} emptyText="No premium estimates generated yet." showQuote />
        </Panel>
      </section>
    </div>
  );
}

function buildStats(leads) {
  const quality = { high: 0, medium: 0, low: 0 };
  for (const lead of leads) {
    const score = lead.lead_quality?.score;
    if (score in quality) quality[score] += 1;
  }

  return {
    total: leads.length,
    pendingApplications: leads.filter((lead) => !lead.completed).length,
    completedQuotes: leads.filter((lead) => lead.completed || lead.ml_quote != null).length,
    meetingRequests: leads.filter((lead) => lead.meeting_requested).length,
    policyUploads: leads.filter((lead) => lead.has_dec_page).length,
    quality,
  };
}

function PageHeader({ eyebrow, title, description }) {
  return (
    <header className="border-b border-white/[0.08] pb-5">
      <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-[#d7ad55]">{eyebrow}</p>
      <h1 className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-white">{title}</h1>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-white/50">{description}</p>
    </header>
  );
}

function MetricCard({ label, value, detail }) {
  return (
    <div className="rounded-xl border border-white/[0.08] bg-[#0f1012] p-4 shadow-[0_18px_60px_rgba(0,0,0,0.18)] transition hover:border-[#d7ad55]/20">
      <p className="text-xs font-medium uppercase tracking-[0.12em] text-white/35">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-[-0.03em] text-white">{value}</p>
      <p className="mt-2 text-sm text-white/42">{detail}</p>
    </div>
  );
}

function Panel({ title, subtitle, children }) {
  return (
    <div className="rounded-xl border border-white/[0.08] bg-[#0f1012] p-5 shadow-[0_18px_60px_rgba(0,0,0,0.18)]">
      <div className="mb-5">
        <h2 className="text-base font-semibold tracking-[-0.01em] text-white">{title}</h2>
        {subtitle && <p className="mt-1 text-sm text-white/42">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

function BarRows({ items, total }) {
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.label}>
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-white/62">{item.label}</span>
            <span className="font-medium text-white">{item.value}</span>
          </div>
          <div className="h-2 rounded-full bg-white/[0.06]">
            <div
              className={`h-2 rounded-full ${item.tone}`}
              style={{ width: `${Math.min(100, (item.value / total) * 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function LeadList({ leads, emptyText, showQuote = false }) {
  if (leads.length === 0) {
    return <p className="rounded-lg border border-white/[0.06] bg-white/[0.025] p-4 text-sm text-white/45">{emptyText}</p>;
  }

  return (
    <div className="divide-y divide-white/[0.07]">
      {leads.map((lead) => (
        <Link
          key={lead.session_id}
          to={`/admin/leads/${lead.session_id}`}
          className="flex items-center justify-between gap-4 py-3 transition hover:bg-white/[0.025]"
        >
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <p className="truncate text-sm font-medium text-white">{lead.name || "Unknown lead"}</p>
              <StatusBadge tone={lead.lead_quality?.score}>{lead.lead_quality?.score || "unknown"}</StatusBadge>
            </div>
            <p className="mt-1 truncate text-xs text-white/40">
              {lead.email || lead.phone || "No contact"} · {lead.insurance_type}
            </p>
            {lead.conversation_summary && (
              <p className="mt-2 line-clamp-2 max-w-xl text-xs leading-5 text-white/42">
                {lead.conversation_summary}
              </p>
            )}
          </div>
          <div className="shrink-0 text-right text-sm text-white/62">
            {showQuote ? formatQuote(lead.ml_quote) : lead.meeting_status || (lead.completed ? "quote complete" : "in progress")}
          </div>
        </Link>
      ))}
    </div>
  );
}

function ErrorPanel({ message }) {
  return (
    <div className="rounded-lg border border-red-400/20 bg-red-500/10 p-3 text-sm text-red-100">
      {message}
    </div>
  );
}

function formatQuote(value) {
  return value == null ? "No quote" : `$${Math.round(Number(value))}/mo`;
}

export default AdminOverview;
