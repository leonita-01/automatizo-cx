import { useCallback, useEffect, useRef, useState } from "react";


export default function useSpeech(language, onTranscript) {
  const recognitionRef = useRef(null);
  const [listening, setListening] = useState(false);

  const Recognition =
    window.SpeechRecognition
    || window.webkitSpeechRecognition;

  const recognitionSupported = Boolean(Recognition);
  const synthesisSupported = "speechSynthesis" in window;

  useEffect(() => {
    if (!Recognition) {
      return undefined;
    }

    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = language === "de" ? "de-DE" : "en-GB";

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };

    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;

    return () => recognition.abort();
  }, [Recognition, language, onTranscript]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current || listening) {
      return;
    }
    setListening(true);
    recognitionRef.current.start();
  }, [listening]);

  const speak = useCallback(
    (text) => {
      if (!synthesisSupported) {
        return;
      }
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === "de" ? "de-DE" : "en-GB";
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    },
    [language, synthesisSupported],
  );

  return {
    listening,
    recognitionSupported,
    synthesisSupported,
    startListening,
    speak,
  };
}
