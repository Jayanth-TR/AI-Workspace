import api from '../api/axios'

export const getChats = async () => (await api.get('/chats/')).data
export const getMessages = async (chatId) => (await api.get(`/chats/${chatId}/messages`)).data
export const startChat = async (content, mode = 'chat') =>
  (await api.post('/chats/messages', { message: content, content, mode })).data
export const sendMessage = async (chatId, content, mode = 'chat') =>
  (await api.post(`/chats/${chatId}/messages`, { message: content, content, mode })).data
export const deleteChat = async (chatId) => (await api.delete(`/chats/${chatId}`)).data
