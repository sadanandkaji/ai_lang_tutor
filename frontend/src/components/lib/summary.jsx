import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import axios from "axios";
import Button from "../ui/Button";

const API_URL = "http://127.0.0.1:8000"; // Update if deploying online

export default function Summary() {
  const [summary, setSummary] = useState([]);
  const navigate = useNavigate(); // Initialize navigation

  useEffect(() => {
    axios
      .get(`${API_URL}/summary/user123`)
      .then((response) => {
        setSummary(response.data.mistakes || []); // Expecting an array of mistakes from API
      })
      .catch(() => {
        setSummary(["Error fetching summary"]);
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-4">Mistake Summary</h1>

      <div className="bg-gray-800 p-4 rounded-lg shadow-lg max-w-lg w-full">
        {summary.length > 0 ? (
          <ul className="space-y-2">
            {summary.map((item, index) => (
              <li key={index} className="bg-gray-700 p-2 rounded-lg shadow">
                <p className="text-red-400">❌ Mistake: {item.mistake}</p>
                <p className="text-green-400">✅ Correction: {item.correction}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No mistakes recorded. Great job! 🎉</p>
        )}
      </div>

      <Button
        onClick={() => navigate("/")}
        className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
      >
        Back to Chat
      </Button>
    </div>
  );
}
