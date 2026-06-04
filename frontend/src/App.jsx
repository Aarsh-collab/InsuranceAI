import { BrowserRouter, Navigate, Route, Routes, useSearchParams } from "react-router-dom";
import AdminLayout from "./components/admin/AdminLayout";
import AdminLeadDetail from "./components/admin/AdminLeadDetail";
import AdminLeads from "./components/admin/AdminLeads";
import AdminLogin from "./components/admin/AdminLogin";
import AdminOverview from "./components/admin/AdminOverview";
import RequireAdminAuth from "./components/admin/RequireAdminAuth";
import AssistantButton from "./components/assistants/AssistantButton";
import AssistantSidebar from "./components/assistants/AssistantSidebar";
import { useAssistantChat } from "./hooks/useAssistantChat";

function DemoPage() {
  const assistant = useAssistantChat({ siteId: "demo", mode: "demo" });

  return (
    <div className="min-h-screen bg-[#08090b] text-white">
      <main>
        <section className="relative overflow-hidden border-b border-white/[0.08]">
          <div className="mx-auto grid min-h-[92vh] max-w-7xl gap-10 px-5 py-8 sm:px-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:py-10">
            <div className="max-w-3xl">
              <nav className="mb-16 flex items-center justify-between gap-4 lg:mb-20">
                <div>
                  <p className="text-base font-semibold tracking-[-0.01em] text-white">InsuranceAI</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.18em] text-[#d7ad55]">Life insurance active</p>
                </div>
                <a
                  href="/admin/login"
                  className="rounded-md border border-white/[0.1] px-3 py-2 text-sm text-white/62 transition hover:border-[#d7ad55]/35 hover:text-white"
                >
                  Broker dashboard
                </a>
              </nav>

              <div className="inline-flex flex-wrap items-center gap-2 rounded-full border border-[#d7ad55]/20 bg-[#d7ad55]/8 px-3 py-2 text-xs font-medium text-[#f2d28c]">
                <span>Preliminary estimate only</span>
                <span className="h-1 w-1 rounded-full bg-[#d7ad55]/60" />
                <span>No SSN required</span>
                <span className="h-1 w-1 rounded-full bg-[#d7ad55]/60" />
                <span>Licensed broker review available</span>
              </div>

              <h1 className="mt-7 max-w-4xl text-5xl font-semibold leading-[1.02] tracking-[-0.04em] text-white sm:text-6xl lg:text-7xl">
                Life insurance intake that feels clear, fast, and broker-ready.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-8 text-white/58 sm:text-lg">
                InsuranceAI guides a consumer through life insurance questions, explains preliminary premium estimates, and organizes the handoff for broker review.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <button
                  type="button"
                  onClick={assistant.openAssistant}
                  className="rounded-md bg-[#c89b3c] px-5 py-3 text-sm font-semibold text-[#111111] shadow-[0_18px_40px_rgba(0,0,0,0.35)] transition hover:brightness-105"
                >
                  {assistant.hasConversation ? "Continue your estimate" : "Try the assistant"}
                </button>
                <a
                  href="#how-it-works"
                  className="rounded-md border border-white/[0.1] px-5 py-3 text-center text-sm font-semibold text-white/72 transition hover:border-white/18 hover:bg-white/[0.035] hover:text-white"
                >
                  See how it works
                </a>
              </div>

              <div className="mt-7 grid gap-2 sm:grid-cols-2">
                <Availability label="Life insurance" status="Active" active />
                <Availability label="Auto, Home, Renters, Health" status="In development" />
              </div>
            </div>

            <DemoPreview hasConversation={assistant.hasConversation} onOpen={assistant.openAssistant} />
          </div>
        </section>

        <section id="how-it-works" className="border-b border-white/[0.08] px-5 py-16 sm:px-8">
          <div className="mx-auto max-w-7xl">
            <SectionHeader
              eyebrow="Workflow"
              title="Built around the actual life insurance intake."
              description="The demo stays narrow on purpose: life insurance first, clean handoff second, additional insurance products later."
            />
            <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <InfoPanel title="Answer intake questions" detail="The assistant collects life insurance basics like age, coverage amount, term, health history, and lifestyle risk." />
              <InfoPanel title="Get a preliminary estimate" detail="The estimate is clearly positioned as preliminary and dependent on final underwriting review." />
              <InfoPanel title="Understand the price" detail="Users can ask why an estimate is higher, lower, or changed, using the details they already provided." />
              <InfoPanel title="Request broker follow-up" detail="A licensed broker can review the intake, conversation history, quote context, and next-step intent." />
            </div>
          </div>
        </section>

        <section className="border-b border-white/[0.08] px-5 py-16 sm:px-8">
          <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
            <SectionHeader
              eyebrow="Broker view"
              title="Lead details arrive organized."
              description="The dashboard focuses on what a broker needs to review quickly: contact details, quote status, missing fields, conversation history, document context, and session summary."
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <Signal label="Coverage interest" value="$500k term life, 20 years" />
              <Signal label="Quote context" value="Preliminary monthly estimate visible" />
              <Signal label="Explanation support" value="Pricing factors can be explained from the saved intake" />
              <Signal label="Handoff intent" value="Broker follow-up requested when user asks" />
              <Signal label="DEC page context" value="Uploaded policy details appear in document review when available" />
              <Signal label="Conversation summary" value="Available for quick review when generated" />
            </div>
          </div>
        </section>

        <section className="border-b border-white/[0.08] px-5 py-16 sm:px-8">
          <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
            <SectionHeader
              eyebrow="Explanations"
              title="The assistant can explain the estimate and policy context."
              description="The goal is not to replace broker judgment. It gives users plain-English explanations, then helps route serious questions to a licensed broker."
            />
            <div className="grid gap-4 md:grid-cols-2">
              <InfoPanel
                title="Premium estimate explanations"
                detail="After a quote exists, users can ask what affected the estimate, why it changed, or which provided details mattered most."
              />
              <InfoPanel
                title="DEC page explanations"
                detail="When a declaration page has been uploaded, parsed policy details can be explained in plain English without inventing missing coverage."
              />
            </div>
          </div>
        </section>

        <section className="px-5 py-14 sm:px-8">
          <div className="mx-auto flex max-w-7xl flex-col gap-5 rounded-xl border border-white/[0.08] bg-[#0f1012] p-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-semibold tracking-[-0.02em]">Ready to test the life insurance flow?</h2>
              <p className="mt-2 text-sm leading-6 text-white/52">
                Start with a preliminary estimate, then decide if a broker should review the intake.
              </p>
            </div>
            <button
              type="button"
              onClick={assistant.openAssistant}
              className="rounded-md bg-[#c89b3c] px-5 py-3 text-sm font-semibold text-[#111111] transition hover:brightness-105"
            >
              Open assistant
            </button>
          </div>
        </section>
      </main>

      <AssistantSidebar
        isOpen={assistant.isOpen}
        messages={assistant.messages}
        isResponding={assistant.isResponding}
        isUploadingDocument={assistant.isUploadingDocument}
        hasConversation={assistant.hasConversation}
        connectionStatus={assistant.connectionStatus}
        errorMessage={assistant.errorMessage}
        onRetry={assistant.retryConnection}
        onClose={assistant.closeAssistant}
        onSendMessage={assistant.sendMessage}
        onUploadDocument={assistant.uploadDocument}
      />
      <AssistantButton
        isOpen={assistant.isOpen}
        hasConversation={assistant.hasConversation}
        onToggle={assistant.toggleAssistant}
      />
    </div>
  );
}

function WidgetPage() {
  const [searchParams] = useSearchParams();
  const siteId = searchParams.get("site_id") || "infygrow_fs";
  const brand = searchParams.get("brand") || "InsuranceAI";
  const assistant = useAssistantChat({ siteId, mode: "widget" });

  return (
    <div className="min-h-[100dvh] bg-[#0b0d10] text-white">
      <AssistantSidebar
        mode="widget"
        brand={brand}
        isOpen
        messages={assistant.messages}
        isResponding={assistant.isResponding}
        isUploadingDocument={assistant.isUploadingDocument}
        hasConversation={assistant.hasConversation}
        connectionStatus={assistant.connectionStatus}
        errorMessage={assistant.errorMessage}
        onRetry={assistant.retryConnection}
        onClose={assistant.closeAssistant}
        onSendMessage={assistant.sendMessage}
        onUploadDocument={assistant.uploadDocument}
      />
    </div>
  );
}

function DemoPreview({ hasConversation, onOpen }) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="group w-full rounded-xl border border-white/[0.08] bg-[#101317] p-4 text-left shadow-[0_24px_80px_rgba(0,0,0,0.35)] transition hover:border-[#d7ad55]/25"
    >
      <div className="rounded-lg border border-white/[0.08] bg-[#15191f] p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-[#d7ad55]">Life assistant</p>
            <h2 className="mt-1 text-lg font-semibold text-white">InsuranceAI</h2>
          </div>
          <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-2.5 py-1 text-[11px] font-medium text-emerald-100">
            Active
          </span>
        </div>
        <div className="mt-8 space-y-3">
          <MessageBubble>Tell me your age and the amount of coverage you are considering.</MessageBubble>
          <MessageBubble user>$500k for 20 years. I am 30 and healthy.</MessageBubble>
          <MessageBubble>Based on your info, I can prepare a preliminary estimate and a broker review path.</MessageBubble>
        </div>
        <div className="mt-8 rounded-lg border border-white/[0.08] bg-[#0f1216] p-3 text-sm text-white/48">
          {hasConversation ? "Welcome back. Continue your estimate." : "Preliminary estimate only. No SSN required."}
        </div>
      </div>
      <p className="mt-4 text-center text-sm font-medium text-[#f2d28c] transition group-hover:text-white">
        Open assistant
      </p>
    </button>
  );
}

function MessageBubble({ children, user = false }) {
  return (
    <div className={`flex ${user ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[84%] rounded-2xl px-4 py-3 text-sm leading-6 ${
          user
            ? "rounded-br-md bg-[#c89b3c] text-[#111111]"
            : "rounded-bl-md border border-white/[0.07] bg-[#1a1f25] text-white/78"
        }`}
      >
        {children}
      </div>
    </div>
  );
}

function Availability({ label, status, active = false }) {
  return (
    <div className="rounded-lg border border-white/[0.08] bg-white/[0.025] p-3">
      <p className="text-sm font-medium text-white">{label}</p>
      <p className={`mt-1 text-xs ${active ? "text-emerald-200" : "text-white/42"}`}>{status}</p>
    </div>
  );
}

function SectionHeader({ eyebrow, title, description }) {
  return (
    <div>
      <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-[#d7ad55]">{eyebrow}</p>
      <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-[-0.03em] text-white md:text-4xl">{title}</h2>
      <p className="mt-4 max-w-2xl text-sm leading-7 text-white/52">{description}</p>
    </div>
  );
}

function InfoPanel({ title, detail }) {
  return (
    <div className="rounded-xl border border-white/[0.08] bg-[#0f1012] p-5">
      <h3 className="text-base font-semibold tracking-[-0.01em] text-white">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-white/52">{detail}</p>
    </div>
  );
}

function Signal({ label, value }) {
  return (
    <div className="rounded-lg border border-white/[0.08] bg-[#0f1012] p-4">
      <p className="text-xs uppercase tracking-[0.14em] text-white/35">{label}</p>
      <p className="mt-2 text-sm font-medium leading-6 text-white/78">{value}</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route
          path="/admin"
          element={
            <RequireAdminAuth>
              <AdminLayout />
            </RequireAdminAuth>
          }
        >
          <Route index element={<AdminOverview />} />
          <Route path="leads" element={<AdminLeads />} />
          <Route path="leads/:sessionId" element={<AdminLeadDetail />} />
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Route>
        <Route path="/widget" element={<WidgetPage />} />
        <Route path="/" element={<DemoPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
