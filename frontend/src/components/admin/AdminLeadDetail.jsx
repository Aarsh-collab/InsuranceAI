import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { fetchLeadDetail } from "../../services/adminApi";
import StatusBadge from "./StatusBadge";

const tabs = ["Overview", "Intake", "Document Review", "Chat"];

function AdminLeadDetail() {
  const { sessionId } = useParams();
  const [lead, setLead] = useState(null);
  const [activeTab, setActiveTab] = useState("Overview");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeadDetail(sessionId)
      .then(setLead)
      .catch((err) => {
        if (err.status === 401) {
          navigate("/admin/login", { replace: true });
          return;
        }
        setError(err.message);
      });
  }, [navigate, sessionId]);

  const application = lead?.state?.application || {};
  const summary = lead?.state?.memory?.session_summary;

  const intakeFields = useMemo(
    () => [
      ["Age", lead?.life_application?.age],
      ["Gender", lead?.life_application?.gender],
      ["BMI", lead?.life_application?.bmi],
      ["Smoker", lead?.life_application?.smoker],
      ["Coverage Amount", money(lead?.life_application?.coverage_amount)],
      ["Term Length", years(lead?.life_application?.term_length)],
      ["Diabetes", yesNo(lead?.life_application?.diabetes)],
      ["High BP", yesNo(lead?.life_application?.high_bp)],
      ["Heart Disease", yesNo(lead?.life_application?.heart_disease)],
      ["Cancer History", yesNo(lead?.life_application?.cancer_history)],
      ["Family History Count", lead?.life_application?.family_history_count],
      ["Alcohol", lead?.life_application?.alcohol],
      ["Driving Violations", lead?.life_application?.driving_violations],
      ["Occupation Risk", lead?.life_application?.occupation],
      ["ZIP Risk", lead?.life_application?.zip_risk],
    ],
    [lead]
  );

  if (error) {
    return (
      <div>
        <Link className="text-sm text-[#d4af57]" to="/admin/leads">
          Back to leads
        </Link>
        <div className="mt-4 rounded-lg border border-rose-400/20 bg-rose-400/10 p-4 text-rose-100">
          {error}
        </div>
      </div>
    );
  }

  if (!lead) {
    return <div className="text-white/55">Loading lead...</div>;
  }

  return (
    <div className="space-y-5">
      <Link className="text-sm font-medium text-[#d7ad55] transition hover:text-[#f2d28c]" to="/admin/leads">
        Back to lead queue
      </Link>

      <header className="rounded-xl border border-white/[0.08] bg-[#0f1012] p-5 shadow-[0_18px_60px_rgba(0,0,0,0.18)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-[#d7ad55]">
              {lead.session.insurance_type} underwriting file
            </p>
            <h1 className="mt-2 text-2xl font-semibold tracking-[-0.02em]">
              {lead.account.name || "Unknown lead"}
            </h1>
            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm text-white/60">
              <span>{lead.account.email || "No email"}</span>
              <span>{lead.account.phone || "No phone"}</span>
              <span>{formatDate(lead.session.created_at)}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatusBadge tone={lead.lead_quality?.score}>
              {lead.lead_quality?.score || "unknown"}
            </StatusBadge>
            <StatusBadge>
              {lead.account.meeting_status ||
                (lead.account.meeting_requested ? "requested" : "no meeting")}
            </StatusBadge>
          </div>
        </div>
      </header>

      <div className="flex flex-wrap gap-2 border-b border-white/[0.08] pb-3">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`rounded-md px-3 py-2 text-xs font-medium uppercase tracking-[0.08em] transition ${
              activeTab === tab
                ? "border border-[#d7ad55]/25 bg-[#d7ad55]/12 text-[#f2d28c]"
                : "border border-white/[0.08] bg-white/[0.025] text-white/50 hover:bg-white/[0.05] hover:text-white/75"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <section>
        {activeTab === "Overview" && (
          <OverviewTab lead={lead} application={application} summary={summary} />
        )}
        {activeTab === "Intake" && (
          <IntakeTab
            fields={intakeFields}
            missingFields={application.missing_fields || []}
            quote={application.ml_quote}
          />
        )}
        {activeTab === "Document Review" && <DocumentTab decPage={lead.dec_page} />}
        {activeTab === "Chat" && <ChatTab messages={lead.messages || []} />}
      </section>
    </div>
  );
}

function OverviewTab({ lead, application, summary }) {
  return (
    <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
      <Panel title="Underwriting Summary">
        <p className="text-sm leading-6 text-white/70">
          {summary || "No long-term session summary has been generated yet."}
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <MiniStat
            label="Quote"
            value={application.ml_quote == null ? "No quote" : `$${Math.round(application.ml_quote)}/mo`}
          />
          <MiniStat label="Completed" value={application.completed ? "Yes" : "No"} />
          <MiniStat label="Policy Upload" value={lead.dec_page ? "Yes" : "No"} />
        </div>
      </Panel>
      <Panel title="Lead Quality Signals">
        <StatusBadge tone={lead.lead_quality?.score}>
          {lead.lead_quality?.score || "unknown"}
        </StatusBadge>
        <ul className="mt-4 space-y-2 text-sm text-white/65">
          {(lead.lead_quality?.reasons || []).map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

function IntakeTab({ fields, missingFields, quote }) {
  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
      <Panel title="Application Intake">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {fields.map(([label, value]) => (
            <div key={label} className="rounded-lg border border-white/[0.06] bg-white/[0.025] p-3">
              <p className="text-xs uppercase tracking-[0.12em] text-white/35">{label}</p>
              <p className="mt-1 text-sm text-white/80">{present(value)}</p>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Quote Status">
        <MiniStat
          label="Estimated Premium"
          value={quote == null ? "No quote" : `$${Math.round(quote)}/mo`}
        />
        <div className="mt-4">
          <p className="mb-2 text-sm font-medium text-white/70">Missing Fields</p>
          {missingFields.length === 0 ? (
            <p className="text-sm text-white/55">None</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {missingFields.map((field) => (
                <StatusBadge key={field}>{field}</StatusBadge>
              ))}
            </div>
          )}
        </div>
      </Panel>
    </div>
  );
}

function DocumentTab({ decPage }) {
  if (!decPage) {
    return (
      <Panel title="Document Review">
        <p className="rounded-lg border border-white/[0.06] bg-white/[0.025] p-4 text-sm text-white/50">
          No policy document uploaded.
        </p>
      </Panel>
    );
  }

  return (
    <Panel title="Document Review">
      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        <MiniStat label="Insurance Type" value={decPage.insurance_type || "-"} />
        <MiniStat label="Uploaded" value={formatDate(decPage.uploaded_at)} />
        <MiniStat label="Document ID" value={decPage.dec_page_id} />
      </div>
      <pre className="max-h-[520px] overflow-auto rounded-lg border border-white/[0.06] bg-black/30 p-4 text-xs leading-5 text-white/70">
        {JSON.stringify(decPage.parsed_json || {}, null, 2)}
      </pre>
    </Panel>
  );
}

function ChatTab({ messages }) {
  return (
    <Panel title="Conversation">
      {messages.length === 0 ? (
        <p className="text-sm text-white/55">No messages yet.</p>
      ) : (
        <div className="space-y-3">
          {messages.map((message) => (
            <div
              key={message.message_id}
              className={`rounded-lg border p-3 ${
                message.role === "user"
                  ? "border-[#d7ad55]/15 bg-[#d7ad55]/10"
                  : "border-white/[0.06] bg-white/[0.035]"
              }`}
            >
              <div className="mb-1 flex items-center justify-between gap-3 text-xs text-white/35">
                <span className="uppercase tracking-[0.12em]">{message.role}</span>
                <span>{formatDateTime(message.created_at)}</span>
              </div>
              <p className="whitespace-pre-wrap text-sm leading-6 text-white/75">
                {message.content}
              </p>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}

function Panel({ title, children }) {
  return (
    <div className="rounded-xl border border-white/[0.08] bg-[#0f1012] p-5 shadow-[0_18px_60px_rgba(0,0,0,0.18)]">
      <h2 className="mb-4 text-base font-semibold tracking-[-0.01em]">{title}</h2>
      {children}
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div className="rounded-lg border border-white/[0.06] bg-white/[0.025] p-3">
      <p className="text-xs uppercase tracking-[0.12em] text-white/35">{label}</p>
      <p className="mt-1 break-words text-sm text-white/80">{present(value)}</p>
    </div>
  );
}

function money(value) {
  return value == null ? null : `$${Number(value).toLocaleString()}`;
}

function years(value) {
  return value == null ? null : `${value} years`;
}

function yesNo(value) {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return null;
}

function present(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatDateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export default AdminLeadDetail;
