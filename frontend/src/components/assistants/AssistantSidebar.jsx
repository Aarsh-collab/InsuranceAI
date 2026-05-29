import ChatInput from "./ChatInput";
import ChatMessages from "./ChatMessages";

function AssistantSidebar({
  isOpen,
  messages,
  isResponding,
  brand = "InsuranceAI",
  mode = "demo",
  hasConversation = false,
  connectionStatus = "idle",
  errorMessage = "",
  isUploadingDocument = false,
  onRetry,
  onClose,
  onSendMessage,
  onUploadDocument,
}) {
  const isEmbedded = mode === "widget";

  return (
    <div className={`${isEmbedded ? "relative h-full min-h-[100dvh]" : "pointer-events-none fixed inset-0 z-50"}`}>
      <button
        type="button"
        aria-label="Close assistant"
        onClick={onClose}
        className={`absolute inset-0 bg-black/45 transition-opacity duration-300 ${
          isOpen ? "pointer-events-auto opacity-100" : "opacity-0"
        } ${isEmbedded ? "hidden" : ""}`}
      />

      <aside
        aria-hidden={!isOpen}
        className={`pointer-events-auto flex flex-col border-white/10 bg-[#101317] shadow-2xl ${
          isEmbedded
            ? "h-[100dvh] w-full border"
            : `absolute right-0 top-0 h-full w-full max-w-[430px] border-l transition-transform duration-300 ease-out ${
                isOpen ? "translate-x-0" : "translate-x-full"
              }`
        }`}
      >
        <header className="border-b border-white/10 px-4 py-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-[#d7ad55]">
                Life assistant
              </p>
              <h2 className="mt-1 text-base font-semibold tracking-[-0.01em] text-white">
                {brand || "InsuranceAI"}
              </h2>
              <p className="mt-1 text-xs leading-5 text-white/45">
                {hasConversation ? "Welcome back. Continue your estimate when ready." : "Preliminary estimate only. No SSN required."}
              </p>
            </div>

            {!isEmbedded && (
              <button
                type="button"
                onClick={onClose}
                aria-label="Close sidebar"
                className="rounded-md p-2 text-white/60 transition hover:bg-white/5 hover:text-white"
              >
                <CloseIcon className="h-4 w-4" />
              </button>
            )}
          </div>
        </header>

        <div className="min-h-0 flex-1">
          <ChatMessages
            messages={messages}
            isResponding={isResponding}
            hasConversation={hasConversation}
            onStarterPrompt={onSendMessage}
          />
        </div>

        <footer className="border-t border-white/10 bg-[#0d1013] p-4">
          {errorMessage && (
            <div className="mb-3 rounded-lg border border-amber-300/20 bg-amber-300/10 p-3 text-xs leading-5 text-amber-100">
              <div>{errorMessage}</div>
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className="mt-2 font-semibold text-[#f2d28c] transition hover:text-white"
                >
                  Retry connection
                </button>
              )}
            </div>
          )}
          <ChatInput
            onSend={onSendMessage}
            onUploadDocument={onUploadDocument}
            disabled={isResponding || isUploadingDocument || connectionStatus === "connecting"}
            uploadDisabled={isResponding || isUploadingDocument || connectionStatus === "connecting"}
            placeholder={hasConversation ? "Continue your estimate..." : "Ask about life insurance..."}
          />
          <p className="mt-3 text-[11px] leading-5 text-white/35">
            Upload a PDF DEC page or ask about your estimate. Preliminary only; broker review available.
          </p>
        </footer>
      </aside>
    </div>
  );
}

export default AssistantSidebar;

function CloseIcon({ className }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      className={className}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M18 6L6 18" />
    </svg>
  );
}
