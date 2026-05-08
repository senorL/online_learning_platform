<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser, loginUser } from '../api/auth'

const router = useRouter()
const isLogin = ref(true)
const form = ref({ username: '', password: '', grade: '七年级' })
const loading = ref(false)

const handleSubmit = async () => {
  if (form.value.username.length < 2) { alert('用户名至少2个字符'); return }
  if (form.value.password.length < 6) { alert('密码至少6位'); return }
  loading.value = true

  try {
    if (isLogin.value) {
      const res = await loginUser({ username: form.value.username, password: form.value.password })
      if (res.data.code === 200) {
        const d = res.data.data
        localStorage.setItem('token', d.access_token)
        localStorage.setItem('username', d.username)
        localStorage.setItem('role', d.role)
        localStorage.setItem('grade', d.grade || '')
        localStorage.setItem('avatar', d.avatar || '')
        router.push('/')
      }
    } else {
      const res = await registerUser(form.value)
      if (res.data.code === 200) {
        alert('注册成功！请登录')
        isLogin.value = true
        form.value.password = ''
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card fade-in">
      <h1 class="login-title"><i class="fas fa-graduation-cap" style="margin-right:8px;color:var(--primary);"></i>{{ isLogin ? '在线学习平台' : '创建新账号' }}</h1>
      <p class="login-subtitle">学-练-测-改 闭环学习系统</p>

      <div class="form-group has-icon">
        <label>用户名</label>
        <i class="fas fa-user form-icon"></i>
        <input v-model="form.username" class="form-input" placeholder="请输入用户名"
          :class="{ error: form.username.length > 0 && form.username.length < 2 }" />
        <p v-if="form.username.length > 0 && form.username.length < 2" class="form-error">用户名至少2个字符</p>
      </div>

      <div v-if="!isLogin" class="form-group">
        <label>所属年级</label>
        <select v-model="form.grade" class="form-select">
          <option value="七年级">七年级</option>
          <option value="八年级">八年级</option>
          <option value="九年级">九年级</option>
        </select>
      </div>

      <div class="form-group has-icon">
        <label>密码</label>
        <i class="fas fa-lock form-icon"></i>
        <input v-model="form.password" type="password" class="form-input" placeholder="请输入密码"
          :class="{ error: form.password.length > 0 && form.password.length < 6 }" />
        <p v-if="form.password.length > 0 && form.password.length < 6" class="form-error">密码至少6位</p>
      </div>

      <button @click="handleSubmit" class="btn btn-primary btn-full" :disabled="loading"
        style="margin-top: 8px; padding: 14px;">
        <i :class="loading ? 'fas fa-spinner fa-spin' : (isLogin ? 'fas fa-sign-in-alt' : 'fas fa-user-plus')"></i>
        {{ isLogin ? '登录系统' : '立即注册' }}
      </button>

      <div style="text-align: center; margin-top: 20px;">
        <button class="link-btn" @click="isLogin = !isLogin">
          {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
        </button>
      </div>
    </div>
  </div>
</template>
