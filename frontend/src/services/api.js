import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

export const fetchArticles = async () => (await api.get('/articles')).data
export const generateArticle = async (payload) => (await api.post('/articles/generate', payload)).data
export const updateArticle = async (id, payload) => (await api.put(`/articles/${id}`, payload)).data
export const deleteArticle = async (id) => (await api.delete(`/articles/${id}`)).data

export const fetchMagazines = async () => (await api.get('/magazines')).data
export const createMagazine = async (payload) => (await api.post('/magazines', payload)).data
export const exportMagazinePdf = async (id) => (await api.post(`/magazines/${id}/export/pdf`)).data
export const exportMagazinePng = async (id) => (await api.post(`/magazines/${id}/export/png`)).data

export default api
