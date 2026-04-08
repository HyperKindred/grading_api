import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 后端地址
  timeout: 30000,
})

export const getProblems = () => api.get('/problems')
export const getProblem = (id) => api.get(`/problems/${id}`)
export const submitCode = (problemId, code) => api.post('/grade', { problem_id: problemId, code })