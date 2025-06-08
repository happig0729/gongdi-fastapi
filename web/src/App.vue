<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <template #header>
        <div class="card-header">
          <h2>工地智能助手</h2>
        </div>
      </template>
      
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" 
             :class="['message', message.role]">
          <el-avatar :icon="message.role === 'user' ? 'User' : 'Assistant'" />
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
      
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题..."
          @keyup.enter.ctrl="sendMessage"
        />
        <el-button type="primary" @click="sendMessage" :loading="loading">
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { chatApi, type ChatMessage } from './api/chat'

const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement>()

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  const userMessage: ChatMessage = {
    role: 'user',
    content: inputMessage.value
  }
  
  messages.value.push(userMessage)
  loading.value = true
  
  try {
    const response = await chatApi.simpleChat({
      prompt: inputMessage.value,
      system_message: '你是一个建筑工地智能助手'
    })
    
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: response.data.answer
    }
    
    messages.value.push(assistantMessage)
    inputMessage.value = ''
    await scrollToBottom()
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.chat-card {
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  background: #f4f4f5;
  padding: 10px 15px;
  border-radius: 8px;
  max-width: 70%;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

.chat-input .el-button {
  align-self: flex-end;
}
</style>
