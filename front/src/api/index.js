import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 60000,
})

export const getProblems = () => api.get('/problems')
export const getProblem = (id) => api.get(`/problems/${id}`)
export const submitCode = (problemId, code, studentId) => 
  api.post('/grade', { problem_id: problemId, code, student_id: studentId })

export const getSubmission = (problemId, studentId) => 
  api.get(`/api/submission?problem_id=${problemId}&student_id=${studentId}`)

export const markRead = (problemId, studentId) => 
  api.post('/api/mark_read', { problem_id: problemId, student_id: studentId })

export const getUsers = () => api.get('/api/users')
export const login = (userId) => api.post('/login', { user_id: userId })
export const getTeacherSubmissions = (problemId) => 
  api.get(`/api/teacher/submissions?problem_id=${problemId}`)
export const updateTeacherSubmission = (problemId, studentId, scores, feedback) =>
  api.post('/api/teacher/update_submission', {
    problem_id: problemId,
    student_id: studentId,
    scores,
    feedback
  })