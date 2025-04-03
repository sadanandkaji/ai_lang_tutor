import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Button from "../ui/Button";
import Input from "../ui/Input";

const API_URL = "http://127.0.0.1:8000"; // Update when deploying

const languages = ["English", "French", "Spanish", "German", "Chinese", "Japanese", "Hindi"];
const proficiencyLevels = ["Basic", "Intermediate", "Expert"];

export default function Dashboard() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [knownLang, setKnownLang] = useState("English");
  const [targetLang, setTargetLang] = useState("French");
  const [proficiency, setProficiency] = useState("Intermediate");
  const [isLoading, setIsLoading] = useState(false);
  const requestRef = useRef(false);
  const navigate = useNavigate();

  const sendMessage = () => {
    if (!message || isLoading || requestRef.current) return;

    requestRef.current = true;
    setIsLoading(true);
    const userMessage = { user_id: "user123", known_lang: knownLang, target_lang: targetLang, message, proficiency };

    setChatHistory((prev) => [...prev, { type: "user", text: message }]);
    setMessage("");

    axios.post(`${API_URL}/chat`, userMessage)
      .then((response) => {
        if (response.data.response) {
          setChatHistory((prev) => [...prev, { type: "bot", text: response.data.response }]);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        setChatHistory((prev) => [...prev, { type: "bot", text: "Error connecting to server." }]);
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

        <div className="flex gap-4 py-2 items-center">
          <div>Known Language</div>
          <select className="p-2 bg-gray-700 text-white rounded" value={knownLang} onChange={(e) => setKnownLang(e.target.value)}>
            {languages.map((lang) => (<option key={lang} value={lang}>{lang}</option>))}
          </select>
          <div>Target Language</div>
          <select className="p-2 bg-gray-700 text-white rounded" value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
            {languages.map((lang) => (<option key={lang} value={lang}>{lang}</option>))}
          </select>
        </div>

        <div className="flex gap-4 py-2 items-center">
          <div>Proficiency Level</div>
          <select className="p-2 bg-gray-700 text-white rounded" value={proficiency} onChange={(e) => setProficiency(e.target.value)}>
            {proficiencyLevels.map((level) => (<option key={level} value={level}>{level}</option>))}
          </select>
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
          <Input className="flex-1 bg-gray-700 text-white p-2 rounded" value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Send a message..." />
          <Button onClick={sendMessage} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded" disabled={isLoading}>
            {isLoading ? "..a sec" : "Send"}
          </Button>
        </div>

        <div className="flex justify-between mt-4">
          <Button onClick={() => navigate("/review")} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
            View Mistake Review
          </Button>
          <Button onClick={() => navigate("/summary")} className="bg-yellow-500 hover:bg-yellow-600 px-4 py-2 rounded">
            View Summary
          </Button>
        </div>
      </div>
    </div>
  );
}