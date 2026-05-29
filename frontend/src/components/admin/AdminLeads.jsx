import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchLeads } from "../../services/adminApi";
import StatusBadge from "./StatusBadge";

const filters = [
  { label: "All", value: "all" },
  { label: "Qualified", value: "qualified" },
  { label: "Incomplete", value: "incomplete" },
  { label: "Low Quality", value: "low" },
  { label: "Meeting Requested", value: "meeting" },
];

function AdminLeads() {
  const [leads, setLeads] = useState([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
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

  const visibleLeads = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return leads.filter((lead) => {
      const matchesQuery =
        !normalized ||
        [lead.name, lead.email, lead.phone, lead.insurance_type, lead.session_id]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(normalized));

      const score = lead.lead_quality?.score;
      const matchesFilter =
        filter === "all" ||
        (filter === "qualified" && score === "high") ||
        (filter === "incomplete" && !lead.completed) ||
        (filter === "low" && score === "low") ||
        (filter === "meeting" && lead.meeting_requested);

      return matchesQuery && matchesFilter;
    });
  }, [filter, leads, query]);

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4 border-b border-white/[0.08] pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-[#d7ad55]">Leads</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-[-0.02em] text-white">Lead Review Queue</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-white/50">
            Search captured sessions, inspect quote status, and open client conversations for review.
          </p>
        </div>
        <div className="rounded-md border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-sm text-white/58">
          {visibleLeads.length} of {leads.length} records
        </div>
      </header>

      {error && (
        <div className="rounded-lg border border-red-400/20 bg-red-500/10 p-3 text-sm text-red-100">
          {error}
        </div>
      )}

      <div className="rounded-xl border border-white/[0.08] bg-[#0f1012] p-4 shadow-[0_18px_60px_rgba(0,0,0,0.18)]">
        <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by name, email, phone, session..."
            className="h-10 w-full rounded-md border border-white/[0.08] bg-[#151618] px-3 text-sm text-white outline-none transition placeholder:text-white/28 focus:border-[#d7ad55]/55 xl:max-w-md"
          />
          <div className="flex flex-wrap gap-2">
            {filters.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setFilter(item.value)}
                className={`rounded-md px-3 py-2 text-xs font-medium uppercase tracking-[0.08em] transition ${
                  filter === item.value
                    ? "border border-[#d7ad55]/25 bg-[#d7ad55]/12 text-[#f2d28c]"
                    : "border border-white/[0.08] bg-white/[0.025] text-white/50 hover:bg-white/[0.05] hover:text-white/75"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-hidden rounded-lg border border-white/[0.07]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px] text-left text-sm">
              <thead className="bg-white/[0.025] text-[11px] uppercase tracking-[0.12em] text-white/35">
                <tr>
                  <th className="px-4 py-3 font-medium">Client</th>
                  <th className="px-4 py-3 font-medium">Contact</th>
                  <th className="px-4 py-3 font-medium">Product</th>
                  <th className="px-4 py-3 font-medium">Premium Estimate</th>
                  <th className="px-4 py-3 font-medium">Quality</th>
                  <th className="px-4 py-3 font-medium">Application</th>
                  <th className="px-4 py-3 font-medium">Missing</th>
                  <th className="px-4 py-3 font-medium">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.07]">
                {visibleLeads.map((lead) => (
                  <tr key={lead.session_id} className="transition hover:bg-white/[0.025]">
                    <td className="px-4 py-4">
                      <Link className="font-medium text-white hover:text-[#f2d28c]" to={`/admin/leads/${lead.session_id}`}>
                        {lead.name || "Unknown client"}
                      </Link>
                      <p className="mt-1 max-w-[220px] truncate text-xs text-white/32">{lead.session_id}</p>
                      {lead.conversation_summary && (
                        <p className="mt-2 max-w-[300px] truncate text-xs text-white/42">{lead.conversation_summary}</p>
                      )}
                    </td>
                    <td className="px-4 py-4 text-white/58">
                      <div>{lead.email || "No email"}</div>
                      <div className="mt-1">{lead.phone || "No phone"}</div>
                    </td>
                    <td className="px-4 py-4 capitalize text-white/70">{lead.insurance_type}</td>
                    <td className="px-4 py-4 text-white/75">{formatQuote(lead.ml_quote)}</td>
                    <td className="px-4 py-4">
                      <StatusBadge tone={lead.lead_quality?.score}>{lead.lead_quality?.score || "unknown"}</StatusBadge>
                    </td>
                    <td className="px-4 py-4">
                      <StatusBadge tone={lead.completed ? "high" : "neutral"}>
                        {lead.completed ? "complete" : "pending"}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-4 text-white/50">{formatMissing(lead.missing_fields)}</td>
                    <td className="px-4 py-4 text-white/50">{formatDate(lead.created_at)}</td>
                  </tr>
                ))}
                {visibleLeads.length === 0 && (
                  <tr>
                    <td className="px-4 py-12 text-center text-white/42" colSpan="8">
                      No leads match this view.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatQuote(value) {
  return value == null ? "No estimate" : `$${Math.round(Number(value))}/mo`;
}

function formatMissing(fields) {
  if (!fields || fields.length === 0) return "None";
  return fields.slice(0, 3).join(", ") + (fields.length > 3 ? ` +${fields.length - 3}` : "");
}

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export default AdminLeads;
