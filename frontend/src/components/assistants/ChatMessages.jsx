import { useEffect, useRef } from "react";

const starterPrompts = [
  "I want a life insurance estimate.",
  "How much coverage should I consider?",
  "Can a broker review this after?",
];

function ChatMessages({ messages, isResponding, hasConversation = false, onStarterPrompt }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [isResponding, messages]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col justify-center px-5 py-8">
        <div className="rounded-xl border border-white/[0.08] bg-white/[0.025] p-4">
          <p className="text-sm font-semibold text-white">
            {hasConversation ? "Welcome back" : "Start a life estimate"}
          </p>
          <p className="mt-2 text-sm leading-6 text-white/48">
            Answer a few life insurance questions, get a preliminary estimate, and choose whether a licensed broker should follow up.
          </p>
        </div>
        <div className="mt-4 space-y-2">
          {starterPrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => onStarterPrompt?.(prompt)}
              className="w-full rounded-lg border border-white/[0.08] bg-[#15191f] px-3 py-3 text-left text-sm text-white/70 transition hover:border-[#d7ad55]/30 hover:bg-[#191e25] hover:text-white"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="sidebar-scroll h-full overflow-y-auto px-4 py-4">
      <div className="space-y-3">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                message.role === "user"
                  ? "rounded-br-md bg-[#c89b3c] text-[#111111]"
                  : message.status === "error"
                    ? "rounded-bl-md border border-amber-300/20 bg-amber-300/10 text-amber-100"
                    : "rounded-bl-md border border-white/[0.06] bg-[#1a1f25] text-white/82"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {isResponding && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-md border border-white/[0.06] bg-[#1a1f25] px-4 py-3 text-sm text-white/65">
              Reviewing...
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>
    </div>
  );
}

export default ChatMessages;
