import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Button from "../ui/Button";
import Input from "../ui/Input";

const API_URL = "http://127.0.0.1:8000";

export default function Dashboard() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [knownLang, setKnownLang] = useState("");
  const [targetLang, setTargetLang] = useState("");
  const [proficiency, setProficiency] = useState("");
  const [setupStep, setSetupStep] = useState(0); // 0: ask knownLang, 1: ask targetLang, 2: ask proficiency, 3: chat
  const [isLoading, setIsLoading] = useState(false);
  const requestRef = useRef(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (chatHistory.length === 0) {
      setChatHistory([{ type: "bot", text: "👋 Hello! What is your known language?" }]);
    }
  }, []);

  const handleSetup = (input) => {
    if (setupStep === 0) {
      setKnownLang(input);
      setChatHistory((prev) => [
        ...prev,
        { type: "bot", text: "Great! Which language do you want to learn?" },
      ]);
      setSetupStep(1);
    } else if (setupStep === 1) {
      setTargetLang(input);
      setChatHistory((prev) => [
        ...prev,
        { type: "bot", text: "Awesome! What is your proficiency level? (Basic / Intermediate / Expert)" },
      ]);
      setSetupStep(2);
    } else if (setupStep === 2) {
      setProficiency(input);
      setChatHistory((prev) => [
        ...prev,
        { type: "bot", text: `You're all set to start chatting in ${input}! 🎉` },
      ]);
      setSetupStep(3);
    }
  };

  const sendMessage = () => {
    if (!message || isLoading || requestRef.current) return;

    const trimmedMessage = message.trim();
    if (!trimmedMessage) return;

    // Add user message immediately
    setChatHistory((prev) => [...prev, { type: "user", text: trimmedMessage }]);
    setMessage("");

    // Setup stage
    if (setupStep < 3) {
      handleSetup(trimmedMessage);
      return;
    }

    // Real chat stage
    requestRef.current = true;
    setIsLoading(true);

    const userMessage = {
      user_id: "user123",
      known_lang: knownLang,
      target_lang: targetLang,
      message: trimmedMessage,
      proficiency,
    };

    axios
      .post(`${API_URL}/chat`, userMessage)
      .then((response) => {
        if (response.data.response) {
          setChatHistory((prev) => [...prev, { type: "bot", text: response.data.response }]);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        setChatHistory((prev) => [
          ...prev,
          { type: "bot", text: "Error connecting to server." },
        ]);
      })
      .finally(() => {
        setIsLoading(false);
        requestRef.current = false;
      });
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
      <div className="w-full max-w-lg bg-gray-800 p-4 rounded-lg shadow-lg flex flex-col h-screen max-h-[90vh]">
        <div className="flex justify-between items-center pb-3 border-b border-gray-700">
          <h1 className="text-xl font-semibold">AI Tutor Chat</h1>
        </div>

        <div className="flex-1 overflow-y-auto border border-gray-600 rounded p-3 flex flex-col gap-2 bg-gray-700">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`px-3 py-2 rounded-xl text-sm max-w-xs break-words shadow-md ${msg.type === "user" ? "bg-blue-500 text-white" : "bg-green-500 text-white"}`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center gap-3 mt-2 p-2 border-t border-gray-700">
          <Input
            className="flex-1 bg-gray-700 text-white p-2 rounded"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <Button
            onClick={sendMessage}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
            disabled={isLoading}
          >
            {isLoading ? "..a sec" : "Send"}
          </Button>
        </div>
      </div>

      <div className="flex justify-between mt-4 w-full max-w-lg">
        <Button onClick={() => navigate("/review")} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded w-full mr-2">
          View Mistake Review
        </Button>
        <Button onClick={() => navigate("/summary")} className="bg-yellow-500 hover:bg-yellow-600 px-4 py-2 rounded w-full ml-2">
          View Summary
        </Button>
      </div>
    </div>
  );
}
