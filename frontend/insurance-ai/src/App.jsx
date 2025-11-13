import { useState } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-black text-white overflow-hidden fixed top-0 left-0">
      {/* Chat Area */}
      <header className="p-4 bg-black text-amber-400 font-semibold text-lg">
          InsurnaceAI
        </header>
      <main className="flex-1 flex flex-col justify-end overflow-y-auto overflow-x-hidden px-6 pb-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-gray-500 text-sm text-center mt-auto">
            [Chat messages will appear here]
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] break-words ${
                  msg.sender === "user"
                    ? "bg-orange-500 text-white px-4 py-2 rounded-2xl rounded-br-none"
                    : "text-white"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))
        )}
      </main>

      {/* Input Bar */}
      <footer className="p-4 bg-black flex gap-2 border-t border-gray-800">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          type="text"
          placeholder="Type your message..."
          className="flex-1 bg-neutral-900 text-white border border-gray-700 rounded-lg p-2 focus:outline-none"
        />
        <button
          onClick={handleSend}
          className="align-right bg-amber-500 px-4 py-2 rounded-lg font-medium hover:bg-orange-400 transition"
        >
          Send
        </button>
      </footer>
    </div>
  );
}

export default App;