import React, { useState } from 'react';
import { generateQuiz } from '../services/api';
import QuizDisplay from '../components/QuizDisplay';

export default function GenerateQuizTab() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quizData, setQuizData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) {
      setError('Please enter a Wikipedia URL.');
      return;
    }

    setLoading(true);
    setError(null);
    setQuizData(null);

    try {
      const response = await generateQuiz(url);
      setQuizData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An unknown error occurred. Is the backend server running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="[https://en.wikipedia.org/wiki/Alan_Turing](https://en.wikipedia.org/wiki/Alan_Turing)"
          className="flex-grow p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 font-semibold text-white bg-blue-600 rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </form>

      {error && (
        <div className="p-4 text-red-800 bg-red-100 border border-red-300 rounded-lg">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="flex justify-center items-center p-10">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent border-solid rounded-full animate-spin"></div>
          <p className="ml-4 text-lg text-gray-600">Generating quiz... This may take a moment.</p>
        </div>
      )}

      {quizData && (
        <div className="mt-6 p-6 bg-white border border-gray-200 rounded-lg shadow-lg">
          <QuizDisplay quizData={quizData} />
        </div>
      )}
    </div>
  );
}
