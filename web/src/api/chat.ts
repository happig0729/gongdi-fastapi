import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  prompt: string
  system_message?: string
  history?: ChatMessage[]
}

export const chatApi = {
  simpleChat: (data: ChatRequest) => {
    return api.post('/chat', data)
  },
  
  functionCall: (query: string) => {
    return api.post('/function_call', { query })
  },
  
  completeFunctionCall: (query: string) => {
    return api.post('/complete_function_call', { query })
  },
  
  multiTurnChat: (data: ChatRequest) => {
    return api.post('/multi_turn_chat', data)
  }
} 