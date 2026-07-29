import api from '../api/axios'
class AuthService {
  async register(userData) { return (await api.post('/auth/register', userData)).data }
  async login({ email, password }) {
    const form = new URLSearchParams({ username: email, password })
    return (await api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })).data
  }
  async getCurrentUser() { return (await api.post('/auth/me')).data }
}
export default new AuthService()
