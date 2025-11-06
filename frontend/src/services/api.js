import axios from 'axios';

// Create an Axios instance pointing to our FastAPI backend
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const generateQuiz = (url) => {
  return apiClient.post('/generate_quiz', { url });
};

export const getHistory = () => {
  return apiClient.get('/history');
};

export const getQuizById = (quiz_id) => {
  return apiClient.get(`/quiz/${quiz_id}`);
};
