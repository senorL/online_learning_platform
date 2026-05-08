<script setup lang="ts">
import { ref, computed, onErrorCaptured, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const username = ref(localStorage.getItem('username') || '')
const role = ref(localStorage.getItem('role') || 'student')
const grade = ref(localStorage.getItem('grade') || '')
const avatar = ref(localStorage.getItem('avatar') || '')

window.addEventListener('profile-updated', () => {
  grade.value = localStorage.getItem('grade') || ''
  avatar.value = localStorage.getItem('avatar') || ''
})

const tabs = [
  { id: 'courses', name: '课程学习', icon: 'fa-tv', path: '/courses' },
  { id: 'quiz', name: '刷题挑战', icon: 'fa-keyboard', path: '/quiz' },
  { id: 'wrong-book', name: '错题收纳', icon: 'fa-folder-open', path: '/wrong-book' },
  { id: 'heatmap', name: '成就勋章', icon: 'fa-medal', path: '/heatmap' },
  { id: 'ranking', name: '排行榜', icon: 'fa-trophy', path: '/ranking' },
  { id: 'profile', name: '个人资料', icon: 'fa-user', path: '/profile' },
]

const adminTabs = [
  { id: 'admin-questions', name: '题库管理', icon: 'fa-database', path: '/admin/questions' },
  { id: 'admin-courses', name: '课程管理', icon: 'fa-book', path: '/admin/courses' },
  { id: 'admin-chapters', name: '章节管理', icon: 'fa-sitemap', path: '/admin/chapters' },
  { id: 'admin-users', name: '用户管理', icon: 'fa-users', path: '/admin/users' },
  { id: 'admin-stats', name: '数据统计', icon: 'fa-chart-bar', path: '/admin/stats' },
]

const visibleTabs = computed(() => {
  if (role.value === 'admin') {
    return adminTabs
  }
  return tabs
})

onErrorCaptured((err) => {
  console.error("LayoutView 捕获到渲染错误:", err)
  // 阻止错误继续向上传播导致白屏
  return false
})

const currentPath = computed(() => route.path)
const currentTitle = computed(() => {
  const tab = visibleTabs.value.find(t => currentPath.value.startsWith(t.path))
  return tab?.name || '首页'
})

const isDark = ref(localStorage.getItem('theme') !== 'light')

const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  localStorage.setItem('theme', theme)
  applyTheme()
}

const applyTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.remove('light-theme')
  } else {
    document.documentElement.classList.add('light-theme')
  }
}

const logout = () => { localStorage.clear(); router.push('/login') }

onMounted(() => {
  applyTheme()
})
</script>

<template>
  <div class="app-layout">
    <aside class="app-sidebar">
      <div class="sidebar-logo">
        <i class="fas fa-graduation-cap" style="margin-right: 8px;"></i>学习平台
      </div>
      <nav class="sidebar-nav">
        <div v-for="tab in visibleTabs" :key="tab.id"
          class="nav-item" :class="{ active: currentPath.startsWith(tab.path) }"
          @click="router.push(tab.path)">
          <i :class="['fas', tab.icon]"></i>
          <span>{{ tab.name }}</span>
        </div>
      </nav>
      <div class="sidebar-footer" style="padding: 16px; border-top: 1px solid var(--border);">
        <div class="nav-item" @click="toggleTheme">
          <i :class="['fas', isDark ? 'fa-sun' : 'fa-moon']"></i>
          <span>{{ isDark ? '明亮模式' : '深色模式' }}</span>
        </div>
      </div>
    </aside>

    <div class="app-main">
      <header class="app-header">
        <h2 class="header-title">{{ currentTitle }}</h2>
        <div class="header-user">
          <div style="text-align: right;">
            <div class="header-username">{{ username }}</div>
            <div class="header-grade">{{ grade }}</div>
          </div>
          <div class="avatar">
            <img v-if="avatar" :src="avatar" />
            <span v-else>{{ (username || '').charAt(0).toUpperCase() }}</span>
          </div>
          <button class="logout-btn" @click="logout" title="退出登录">
            <i class="fas fa-power-off"></i>
          </button>
        </div>
      </header>
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>
