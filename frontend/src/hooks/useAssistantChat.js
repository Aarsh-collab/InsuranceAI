import { useEffect, useMemo, useState } from "react";
import { createChatSession, sendChatMessage, uploadDecPage } from "../services/chatApi";

const readStoredJson = (key, fallback) => {
  try {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : fallback;
  } catch {
    return fallback;
  }
};

const storageSafe = (value) =>
  String(value || "demo")
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "_")
    .replace(/^_+|_+$/g, "") || "demo";

export function buildAssistantStorageKey({ mode, siteId, suffix }) {
  return `insuranceai_${storageSafe(mode)}_${storageSafe(siteId)}_chat_${suffix}`;
}

export function useAssistantChat({ siteId = "demo", mode = "demo" } = {}) {
  const keys = useMemo(
    () => ({
      isOpen: buildAssistantStorageKey({ mode, siteId, suffix: "is_open" }),
      messages: buildAssistantStorageKey({ mode, siteId, suffix: "messages" }),
      session: buildAssistantStorageKey({ mode, siteId, suffix: "session" }),
    }),
    [mode, siteId]
  );

  const [isOpen, setIsOpen] = useState(() => readStoredJson(keys.isOpen, false));
  const [messages, setMessages] = useState(() => readStoredJson(keys.messages, []));
  const [chatSession, setChatSession] = useState(() => readStoredJson(keys.session, null));
  const [isResponding, setIsResponding] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [isUploadingDocument, setIsUploadingDocument] = useState(false);

  useEffect(() => {
    setIsOpen(readStoredJson(keys.isOpen, false));
    setMessages(readStoredJson(keys.messages, []));
    setChatSession(readStoredJson(keys.session, null));
    setErrorMessage("");
    setConnectionStatus("idle");
  }, [keys.isOpen, keys.messages, keys.session]);

  useEffect(() => {
    localStorage.setItem(keys.messages, JSON.stringify(messages));
  }, [keys.messages, messages]);

  useEffect(() => {
    localStorage.setItem(keys.session, JSON.stringify(chatSession));
  }, [chatSession, keys.session]);

  useEffect(() => {
    localStorage.setItem(keys.isOpen, JSON.stringify(isOpen));
  }, [isOpen, keys.isOpen]);

  const hasConversation = messages.length > 0 || Boolean(chatSession);

  const ensureChatSession = async () => {
    if (chatSession) {
      return chatSession;
    }

    setConnectionStatus("connecting");
    try {
      const session = await createChatSession({ siteId });
      setChatSession(session);
      setConnectionStatus("connected");
      return session;
    } catch (error) {
      setConnectionStatus("unavailable");
      setErrorMessage(
        "The assistant is not reachable right now. Please check the connection and try again."
      );
      throw error;
    }
  };

  const sendMessage = async (content) => {
    const trimmed = content.trim();

    if (!trimmed || isResponding) {
      return;
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      { role: "user", content: trimmed },
    ]);
    setIsResponding(true);
    setErrorMessage("");

    try {
      const session = await ensureChatSession();
      const assistantResponse = await sendChatMessage({
        sessionId: session.sessionId,
        message: trimmed,
      });

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: assistantResponse,
        },
      ]);
      setConnectionStatus("connected");
    } catch {
      setConnectionStatus("unavailable");
      setErrorMessage("Your message did not send. Please retry when the assistant reconnects.");
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          status: "error",
          content:
            "I could not send that message. Your conversation is saved here, and you can try again in a moment.",
        },
      ]);
    } finally {
      setIsResponding(false);
    }
  };

  const uploadDocument = async (file) => {
    if (!file || isUploadingDocument) {
      return;
    }

    if (file.type !== "application/pdf") {
      setErrorMessage("Please upload a PDF declaration page.");
      return;
    }

    setIsUploadingDocument(true);
    setErrorMessage("");
    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "user",
        content: `Uploaded DEC page: ${file.name}`,
      },
    ]);

    try {
      const session = await ensureChatSession();
      await uploadDecPage({ sessionId: session.sessionId, file });
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content:
            "I uploaded and reviewed the declaration page. You can ask what it means, whether anything looks missing, or have a licensed broker review it with your intake.",
        },
      ]);
      setConnectionStatus("connected");
    } catch {
      setConnectionStatus("unavailable");
      setErrorMessage("The declaration page did not upload. Please retry with a PDF.");
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          status: "error",
          content:
            "I could not upload that document. Your conversation is still saved, and you can retry with a PDF declaration page.",
        },
      ]);
    } finally {
      setIsUploadingDocument(false);
    }
  };

  return {
    isOpen,
    setIsOpen,
    messages,
    isResponding,
    isUploadingDocument,
    connectionStatus,
    errorMessage,
    hasConversation,
    openAssistant: () => setIsOpen(true),
    closeAssistant: () => setIsOpen(false),
    toggleAssistant: () => setIsOpen((current) => !current),
    sendMessage,
    uploadDocument,
    retryConnection: () => {
      setErrorMessage("");
      void ensureChatSession();
    },
  };
}
