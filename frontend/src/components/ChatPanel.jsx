import { useState } from "react";
import { Bot, SendHorizonal } from "lucide-react";
import { askEarthLens } from "../api";

export default function ChatPanel({ scanData, userType, city }) {
  const [message, setMessage] = useState("What does NDVI mean?");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    if (!message.trim()) return;

    setLoading(true);

    try {
      const result = await askEarthLens({
        message,
        city,
        user_type: userType,
        green_pct: scanData?.metrics?.green_pct,
        dense_pct: scanData?.metrics?.dense_pct,
        mean_ndvi: scanData?.metrics?.mean_ndvi,
      });

      setAnswer(result.answer);
    } catch (error) {
      setAnswer("EarthLens assistant could not connect. Check backend terminal.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="chat-panel glass">
      <div className="chat-title">
        <div className="bot-orb">
          <Bot size={24} />
        </div>
        <div>
          <span>Ask EarthLens</span>
          <h2>Satellite science, translated.</h2>
        </div>
      </div>

      <div className="prompt-row">
        <button onClick={() => setMessage("Explain this like I am 8")}>
          Explain like I am 8
        </button>
        <button onClick={() => setMessage("What does this mean for urban heat risk?")}>
          Heat risk
        </button>
        <button onClick={() => setMessage("What are the scientific limitations?")}>
          Research caveats
        </button>
      </div>

      <div className="chat-input">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") handleAsk();
          }}
        />
        <button onClick={handleAsk}>
          {loading ? "Thinking..." : "Ask"}
          <SendHorizonal size={17} />
        </button>
      </div>

      {answer && <div className="answer-box">{answer}</div>}
    </section>
  );
}