import React, { useState, useEffect } from 'react';
import { getHistory, getQuizById } from '../services/api';
import Modal from '../components/Modal';
import QuizDisplay from '../components/QuizDisplay';

export default function HistoryTab() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getHistory();
      setHistory(response.data);
    } catch (err) {
      setError('Failed to fetch history.');
    } finally {
      setLoading(false);
    }
  };

  const handleDetailsClick = async (quizId) => {
    try {
      setModalLoading(true);
      setIsModalOpen(true);
      setSelectedQuiz(null);
      const response = await getQuizById(quizId);
      setSelectedQuiz(response.data);
    } catch (err) {
      setError('Failed to fetch quiz details.');
      setIsModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedQuiz(null);
  };

  if (loading) return <p className="text-gray-600">Loading history...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200 shadow-md rounded-lg">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Title</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">URL</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Date</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {history.length === 0 ? (
            <tr>
              <td colSpan="4" className="px-6 py-4 text-center text-gray-500">No quizzes generated yet.</td>
            </tr>
          ) : (
            history.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.title}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 truncate max-w-xs">{item.url}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(item.date_generated).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleDetailsClick(item.id)}
                    className="px-4 py-1 text-sm text-blue-600 bg-blue-100 rounded-full hover:bg-blue-200"
                  >
                    Details
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      <Modal isOpen={isModalOpen} onClose={closeModal}>
        {modalLoading && <p>Loading quiz details...</p>}
        {selectedQuiz && <QuizDisplay quizData={selectedQuiz} />}
      </Modal>
    </div>
  );
}