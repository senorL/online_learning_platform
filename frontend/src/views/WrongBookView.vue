<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMistakes, removeMistake, aiExplain, getReview, markReviewed } from '../api/wrongQuestions'

const mistakes = ref<any[]>([])
const reviewList = ref<any[]>([])
const activeTab = ref<'all' | 'review'>('all')
const aiModal = ref(false)
const aiContent = ref('')
const aiLoading = ref(false)

const loadMistakes = async () => {
  const res = await getMistakes()
  if (res.data.code === 200) mistakes.value = res.data.data
}

const loadReview = async () => {
  const res = await getReview()
  if (res.data.code === 200) reviewList.value = res.data.data
}

const handleRemove = async (id: number) => {
  if (!confirm('确定要移除这道错题吗？')) return
  const res = await removeMistake(id)
  if (res.data.code === 200) loadMistakes()
}

const handleAI = async (id: number) => {
  aiLoading.value = true
  aiModal.value = true
  aiContent.value = '正在思考中...'
  const res = await aiExplain(id)
  if (res.data.code === 200) aiContent.value = res.data.data.explanation
  else aiContent.value = 'AI讲解暂时不可用'
  aiLoading.value = false
}

const handleReview = async (id: number) => {
  const res = await markReviewed(id)
  if (res.data.code === 200) { alert('已完成复习！'); loadReview() }
}

const parseOptions = (str: string) => {
  try { return JSON.parse(str) } catch { return {} }
}

onMounted(() => { loadMistakes(); loadReview() })
</script>

<template>
  <div class="fade-in">
    <div class="filter-tabs" style="margin-bottom: 24px;">
      <button class="filter-tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
        <i class="fas fa-list"></i> 全部错题 ({{ mistakes.length }})
      </button>
      <button class="filter-tab" :class="{ active: activeTab === 'review' }" @click="activeTab = 'review'">
        <i class="fas fa-redo"></i> 今日复习 ({{ reviewList.length }})
      </button>
    </div>

    <template v-if="activeTab === 'all'">
      <div class="grid-2">
        <div v-for="m in mistakes" :key="m.id" class="card mistake-card">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:12px;">
            <span class="question-tag choice">{{ m.subject }}</span>
            <div style="display:flex;gap:8px;">
              <button class="btn btn-sm btn-accent" @click="handleAI(m.id)" title="AI讲解">
                <i class="fas fa-robot"></i>
              </button>
              <button class="btn btn-sm btn-danger" @click="handleRemove(m.id)" title="移除">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          <p style="font-weight:600;margin-bottom:12px;line-height:1.7;">{{ m.content }}</p>
          <div class="mistake-answer">
            <i class="fas fa-times-circle"></i> 你的答案：{{ m.wrong_answer }}
          </div>
          <div class="correct-answer">
            <i class="fas fa-check-circle"></i> 正确答案：{{ m.answer }}
          </div>
          <div v-if="m.explanation" style="margin-top:12px;font-size:13px;color:var(--text-muted);">
            <i class="fas fa-lightbulb" style="color:var(--warning);margin-right:4px;"></i> {{ m.explanation }}
          </div>
        </div>
      </div>
      <div v-if="mistakes.length === 0" class="empty-state">
        <div class="empty-icon"><i class="fas fa-check-double"></i></div>
        <div class="empty-text">太棒了！没有错题记录</div>
      </div>
    </template>

    <template v-if="activeTab === 'review'">
      <div class="grid-2">
        <div v-for="r in reviewList" :key="r.id" class="card">
          <span class="question-tag choice">{{ r.subject }} · 第{{ r.review_count + 1 }}次复习</span>
          <p style="font-weight:600;margin:12px 0;line-height:1.7;">{{ r.content }}</p>
          <button class="btn btn-primary btn-sm" @click="handleReview(r.id)">
            <i class="fas fa-check"></i> 已完成复习
          </button>
        </div>
      </div>
      <div v-if="reviewList.length === 0" class="empty-state">
        <div class="empty-icon"><i class="fas fa-calendar-check"></i></div>
        <div class="empty-text">今天没有需要复习的错题</div>
      </div>
    </template>

    <!-- AI讲解弹窗 -->
    <div v-if="aiModal" class="modal-overlay" @click.self="aiModal = false">
      <div class="modal-content" style="position:relative;">
        <button class="modal-close" @click="aiModal = false"><i class="fas fa-times"></i></button>
        <h3 class="modal-title"><i class="fas fa-robot" style="color:var(--accent);margin-right:8px;"></i>AI讲解</h3>
        <div style="white-space:pre-wrap;line-height:1.8;color:var(--text-muted);">
          <i v-if="aiLoading" class="fas fa-spinner fa-spin" style="margin-right:8px;"></i>
          {{ aiContent }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
