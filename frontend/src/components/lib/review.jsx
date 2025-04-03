import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Button from "../ui/Button";

const API_URL = "http://127.0.0.1:8000"; // Replace with actual backend URL

export default function Review() {
  const [review, setReview] = useState({ summary: [], focus_areas: [], level: "Calculating..." });
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${API_URL}/review/user123`)
      .then((response) => {
        const data = response.data;
        const totalMistakes = data.summary.reduce((sum, item) => sum + item.count, 0);

        let level = "Beginner";
        if (totalMistakes <= 5) level = "Expert";
        else if (totalMistakes <= 15) level = "Intermediate";

        setReview({ ...data, level });
      })
      .catch(() => {
        setReview({ summary: [], focus_areas: [], level: "Unknown" });
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-4">Mistake Review</h1>

      {/* Proficiency Level */}
      <div className="bg-gray-800 p-4 rounded-lg shadow-lg max-w-lg w-full text-center">
        <h2 className="text-xl font-semibold mb-2">Your Proficiency Level</h2>
        <p className={`text-lg font-bold ${review.level === "Beginner" ? "text-red-400" : review.level === "Intermediate" ? "text-yellow-400" : "text-green-400"}`}>
          {review.level}
        </p>

        {/* Progress Bar */}
        <div className="w-full bg-gray-700 rounded-full h-4 mt-2">
          <div
            className={`h-4 rounded-full transition-all ${review.level === "Beginner" ? "bg-red-500 w-1/4" : review.level === "Intermediate" ? "bg-yellow-500 w-2/4" : "bg-green-500 w-3/4"}`}
          ></div>
        </div>
      </div>

      {/* Mistake Summary */}
      {review.summary.length > 0 ? (
        <div className="bg-gray-800 p-4 rounded-lg shadow-lg max-w-lg w-full mt-4">
          <h2 className="text-xl font-semibold mb-2">Mistake Summary</h2>
          <ul className="space-y-2">
            {review.summary.map((item, index) => (
              <li key={index} className="bg-gray-700 p-2 rounded-lg shadow">
                <p className="text-red-400">❌ Mistake: {item.mistake}</p>
                <p className="text-yellow-300">🔁 Occurrences: {item.count}</p>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="mt-4">No mistakes recorded. Great job! 🎉</p>
      )}

      {/* Focus Areas */}
      {review.focus_areas.length > 0 && (
        <div className="bg-gray-800 p-4 mt-4 rounded-lg shadow-lg max-w-lg w-full">
          <h2 className="text-xl font-semibold mb-2">Focus Areas</h2>
          <ul className="space-y-2">
            {review.focus_areas.map((item, index) => (
              <li key={index} className="bg-gray-700 p-2 rounded-lg shadow">
                <p className="text-green-400">⚡ Work on: {item}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      <Button
        onClick={() => navigate("/")}
        className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
      >
        Back to Home
      </Button>
    </div>
  );
}
