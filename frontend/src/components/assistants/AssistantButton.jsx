function AssistantButton({ isOpen, onToggle, hasConversation = false }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isOpen ? "Close assistant" : "Open assistant"}
      className="fixed bottom-6 right-6 z-40 flex items-center gap-3 rounded-full border border-[#d4af57]/30 bg-[#c89b3c] px-4 py-3 text-[#111111] shadow-[0_18px_40px_rgba(0,0,0,0.42)] transition hover:brightness-105 focus:outline-none focus:ring-2 focus:ring-[#f0cf7a] focus:ring-offset-2 focus:ring-offset-[#0b0d10]"
    >
      <BotIcon className="h-6 w-6" />
      <span className="hidden text-sm font-semibold sm:inline">
        {hasConversation ? "Continue estimate" : "Try assistant"}
      </span>
    </button>
  );
}

export default AssistantButton;

function BotIcon({ className }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      className={className}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3v3m-5 5h10a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.25 14h.01M14.75 14h.01M9.5 17h5"
      />
    </svg>
  );
}
