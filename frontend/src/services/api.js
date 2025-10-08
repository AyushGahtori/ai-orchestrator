import axios from 'axios'

const API_KEY = process.env.REACT_APP_API_KEY || 'demo_key'
const BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000'

const client = axios.create({
    baseURL: BASE,
    headers: {
        'X-API-KEY': API_KEY,
    }
})

export default client
