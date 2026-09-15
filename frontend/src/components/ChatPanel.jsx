import { useCallback, useState } from "react";
import {
  Bot,
  Languages,
  Mic,
  MicOff,
  Send,
  ShieldAlert,
  Volume2,
} from "lucide-react";

import useSpeech from "../hooks/useSpeech";
import { api } from "../services/api";


const STARTERS = {
  en: [
    "Where can I view my invoice?",
    "My internet connection is offline",
    "I want to cancel my contract",
  ],
  de: [
    "Wo finde ich meine Rechnung?",
    "Mein Internet funktioniert nicht",
    "Ich möchte meinen Vertrag kündigen",
  ],
};


export default function ChatPanel({ onConversation }) {
  const [language, setLanguage] = useState("en");
  const [draft, setDraft] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! How can I help with your service today?",
    },
  ]);

  const acceptTranscript = useCallback((transcript) => setDraft(transcript), []);
  const speech = useSpeech(language, acceptTranscript);

  async function sendMessage(message = draft) {
    const cleaned = message.trim();
    if (!cleaned || loading) return;

    setDraft("");
    setError("");
    setLoading(true);
    setMessages((current) => [
      ...current,
      { role: "customer", text: cleaned },
    ]);

    try {
      const response = await api.sendChat({
        message: cleaned,
        language,
        conversation_id: conversationId,
      });
      setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: response.answer,
          metadata: response,
        },
      ]);
      if (autoSpeak) speech.speak(response.answer);
      onConversation?.();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  function changeLanguage() {
    const nextLanguage = language === "en" ? "de" : "en";
    setLanguage(nextLanguage);
    setMessages([
      {
        role: "assistant",
        text:
          nextLanguage === "de"
            ? "Hallo! Wie kann ich Ihnen heute helfen?"
            : "Hello! How can I help with your service today?",
      },
    ]);
    setConversationId(null);
  }

  return (
    <section className="panel chat-panel">
      <div className="panel-heading">
        <div>
          <span className="heading-icon"><Bot size={20} /></span>
          <div>
            <h2>Multilingual AI Assistant</h2>
            <p>Grounded answers, security checks and human escalation</p>
          </div>
        </div>
        <div className="chat-controls">
          <label className="speak-toggle">
            <input
              type="checkbox"
              checked={autoSpeak}
              disabled={!speech.synthesisSupported}
              onChange={(event) => setAutoSpeak(event.target.checked)}
            />
            <Volume2 size={14} /> Voice reply
          </label>
          <button className="secondary-button" onClick={changeLanguage}>
            <Languages size={15} /> {language.toUpperCase()}
          </button>
        </div>
      </div>

      <div className="starter-row">
        {STARTERS[language].map((starter) => (
          <button key={starter} onClick={() => sendMessage(starter)}>
            {starter}
          </button>
        ))}
      </div>

      <div className="messages" aria-live="polite">
        {messages.map((message, index) => (
          <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
            <p>{message.text}</p>
            {message.metadata && (
              <div className="message-metadata">
                <span>{message.metadata.intent.replaceAll("_", " ")}</span>
                <span>{Math.round(message.metadata.confidence * 100)}% confidence</span>
                <span>{message.metadata.latency_ms} ms</span>
                {message.metadata.escalation_required && (
                  <span className="escalated">Agent handoff created</span>
                )}
              </div>
            )}
            {message.metadata?.security_flags?.length > 0 && (
              <div className="security-notice">
                <ShieldAlert size={14} /> Security policy activated
              </div>
            )}
            {message.metadata?.sources?.length > 0 && (
              <div className="sources">
                {message.metadata.sources.map((source) => (
                  <span key={source.article_id}>Source: {source.title}</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message assistant"><p>Checking approved knowledge…</p></div>}
      </div>

      {error && <div className="inline-error">{error}</div>}

      <div className="composer">
        <button
          className={`voice-button ${speech.listening ? "listening" : ""}`}
          onClick={speech.startListening}
          disabled={!speech.recognitionSupported || speech.listening}
          title={speech.recognitionSupported ? "Speak your question" : "Voice input is not supported by this browser"}
        >
          {speech.recognitionSupported ? <Mic size={18} /> : <MicOff size={18} />}
        </button>
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => event.key === "Enter" && sendMessage()}
          placeholder={
            speech.listening
              ? "Listening…"
              : language === "en"
                ? "Ask a customer-support question…"
                : "Stellen Sie eine Supportfrage…"
          }
          aria-label="Customer message"
        />
        <button className="primary-button send-button" onClick={() => sendMessage()}>
          <Send size={17} /> Send
        </button>
      </div>
      <small className="privacy-line">
        Personal data is redacted before storage. Conversation: {conversationId || "new"}
      </small>
    </section>
  );
}
