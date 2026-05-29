import { useState } from "react";

function ChatInput({
  onSend,
  onUploadDocument,
  disabled,
  uploadDisabled,
  placeholder = "Type a message...",
}) {
  const [input, setInput] = useState("");

  const handleSubmit = () => {
    const trimmed = input.trim();

    if (!trimmed || disabled) {
      return;
    }

    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex items-end gap-2">
      <label
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-[#171b21] text-white/58 transition ${
          uploadDisabled
            ? "cursor-not-allowed opacity-50"
            : "cursor-pointer hover:border-[#d7ad55]/45 hover:text-[#f2d28c]"
        }`}
        title="Upload a PDF declaration page"
      >
        <input
          type="file"
          accept="application/pdf"
          disabled={uploadDisabled}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              onUploadDocument?.(file);
            }
            event.target.value = "";
          }}
          className="sr-only"
        />
        <UploadIcon className="h-4 w-4" />
      </label>
      <input
        type="text"
        value={input}
        disabled={disabled}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="h-11 flex-1 rounded-lg border border-white/10 bg-[#171b21] px-4 text-sm text-white outline-none transition placeholder:text-white/35 focus:border-[#d4af57] disabled:cursor-not-allowed disabled:opacity-60"
      />

      <button
        type="button"
        onClick={handleSubmit}
        disabled={!input.trim() || disabled}
        className="h-11 rounded-lg bg-[#c89b3c] px-4 text-sm font-semibold text-[#111111] transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <span className="sr-only">Send</span>
        <SendIcon className="h-4 w-4" />
      </button>
    </div>
  );
}

export default ChatInput;

function SendIcon({ className }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      className={className}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h13M13 6l6 6-6 6" />
    </svg>
  );
}

function UploadIcon({ className }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      className={className}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0 4 4m-4-4-4 4" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 16v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" />
    </svg>
  );
}
