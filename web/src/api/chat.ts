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

export interface FunctionCallRequest {
  query: string
  tools?: Array<{
    type?: string
    function?: {
      name: string
      description?: string
      parameters?: Record<string, any>
    }
  }>
}

export const chatApi = {
  simpleChat: (data: ChatRequest) => {
    return api.post('/chat', data)
  },
  
  functionCall: (data: FunctionCallRequest) => {
    return api.post('/function_call', data)
  },
  
  completeFunctionCall: (query: string) => {
    return api.post('/complete_function_call', { query })
  },
  
  multiTurnChat: (data: ChatRequest) => {
    return api.post('/multi_turn_chat', data)
  }
} 