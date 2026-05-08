<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Spin } from '@kousum/semi-ui-vue'
import { generateQuestions, submitAnswer } from '../api/questions'
import catalogData from '../assets/catalog.json'

const userGrade = localStorage.getItem('grade') || '七年级'
const subjects = computed(() => {
  if (userGrade === '七年级') return ['数学', '语文', '英语', '道德与法治', '生物', '地理']
  if (userGrade === '八年级') return ['数学', '语文', '英语', '道德与法治', '物理', '生物', '地理']
  return ['数学', '语文', '英语', '道德与法治', '物理', '化学', '生物', '地理']
})
const currentSubject = ref('数学')
const questions = ref<any[]>([])
const selectedChapter = ref<any>(null)
const selectedPath = ref('')
const selectedDifficulty = ref('medium')
const selectedTypes = ref<string[]>(['choice', 'fill_blank'])
const isLoading = ref(false)
const loadingMessage = ref('正在获取题目...')
const errorMessage = ref('')

// 填空题答案输入
const fillAnswers = ref<Record<number, string>>({})

const currentCatalog = computed(() => {
  return catalogData.find((s: any) => s.title === currentSubject.value) || null
})

const selectSubject = (s: string) => {
  currentSubject.value = s
  selectedChapter.value = null
  questions.value = []
  errorMessage.value = ''
}

const selectSubChapter = (subChapter: any, gradeTitle: string, chapterTitle?: string) => {
  selectedChapter.value = subChapter
  if (chapterTitle && chapterTitle !== subChapter.title) {
    selectedPath.value = `${gradeTitle} - ${chapterTitle} - ${subChapter.title}`
  } else {
    selectedPath.value = `${gradeTitle} - ${subChapter.title}`
  }
  // 自动加载题目
  loadQuestions()
}

const loadQuestions = async () => {
  if (!selectedChapter.value) return
  
  isLoading.value = true
  loadingMessage.value = '正在检索题库...'
  errorMessage.value = ''
  questions.value = []
  fillAnswers.value = {}

  try {
    // 短暂延迟后更新消息，表示可能在等待AI
    const timer = setTimeout(() => {
      loadingMessage.value = 'AI正在为你精心出题，请稍候...'
    }, 2000)

    const res = await generateQuestions({
      subject: currentSubject.value,
      chapter: selectedChapter.value.title,
      difficulty: selectedDifficulty.value,
      types: selectedTypes.value,
      count: 10,
    })

    clearTimeout(timer)

    if (res.data.code === 200 && res.data.data) {
      questions.value = res.data.data
    } else {
      errorMessage.value = res.data.message || '获取题目失败'
    }
  } catch (e: any) {
    errorMessage.value = e.response?.data?.message || '请求超时或网络错误，请重试'
  } finally {
    isLoading.value = false
  }
}

const parseOptions = (str: string) => {
  try { return JSON.parse(str) } catch { return {} }
}

const handleSubmit = async (qid: number, answer: string) => {
  const res = await submitAnswer({ 
    question_id: qid, 
    user_answer: answer,
    subject: currentSubject.value
  })
  if (res.data.code === 200) {
    const d = res.data.data
    if (d.is_correct) {
      alert(`回答正确! 获得${d.points}分`)
    } else {
      alert(`答错了, 正确答案是: ${d.correct_answer}\n${d.explanation || ''}\n已自动收入错题本`)
    }
  }
}

const handleFillSubmit = (q: any) => {
  const answer = fillAnswers.value[q.id]
  if (!answer || !answer.trim()) {
    alert('请输入答案')
    return
  }
  handleSubmit(q.id, answer.trim())
}

const difficultyLabel = (d: string) => {
  if (d === 'easy') return '简单'
  if (d === 'hard') return '困难'
  return '中等'
}

const typeLabel = (t: string) => {
  if (t === 'choice') return '选择题'
  if (t === 'fill_blank') return '填空题'
  return '解答题'
}

const toggleType = (t: string) => {
  const idx = selectedTypes.value.indexOf(t)
  if (idx > -1) {
    if (selectedTypes.value.length > 1) {
      selectedTypes.value.splice(idx, 1)
    }
  } else {
    selectedTypes.value.push(t)
  }
}

onMounted(() => {})
</script>

<template>
  <div class="fade-in">
    <div class="filter-tabs">
      <button v-for="s in subjects" :key="s"
        class="filter-tab" :class="{ active: currentSubject === s }"
        @click="selectSubject(s)">{{ s }}</button>
    </div>

    <div style="display:flex; gap: 24px; align-items: flex-start; margin-top: 20px;">
      <!-- 左侧目录树 -->
      <div class="card" style="width: 320px; padding: 16px; flex-shrink: 0; max-height: 80vh; overflow-y: auto;">
        <h4 style="margin-bottom: 16px; font-weight: 700; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
          <i class="fas fa-list-ul"></i> {{ currentSubject }} 目录
        </h4>
        <div v-if="currentCatalog">
          <div v-for="(grade, gIdx) in currentCatalog.children" :key="gIdx" style="margin-bottom: 12px;">
            <div style="font-weight: 600; color: var(--primary-light); margin-bottom: 8px;">
              {{ grade.title }}
            </div>
            <div v-for="(chapter, cIdx) in grade.children" :key="cIdx" style="margin-left: 12px; margin-bottom: 8px;">
              <template v-if="chapter.children && chapter.children.length > 0">
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 6px;">{{ chapter.title }}</div>
                <div style="margin-left: 12px;">
                    <div v-for="(sub, sIdx) in chapter.children" :key="sIdx"
                      class="catalog-item"
                      :class="{ active: selectedChapter?.title === sub.title }"
                      @click="selectSubChapter(sub, grade.title, chapter.title)">
                      {{ sub.title }}
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="catalog-item"
                    :class="{ active: selectedChapter?.title === chapter.title }"
                    @click="selectSubChapter(chapter, grade.title)">
                    {{ chapter.title }}
                  </div>
                </template>
            </div>
          </div>
        </div>
        <div v-else class="empty-state" style="padding: 20px 0;">暂无目录数据</div>
      </div>

      <!-- 右侧内容区 -->
      <div style="flex: 1;">
        <div v-if="selectedChapter">
          <h3 style="margin-bottom: 16px; font-weight: 700;">
            正在练习: {{ selectedChapter.title }}
          </h3>

          <!-- 难度选择 + 题型选择 -->
          <div class="card" style="margin-bottom: 20px; padding: 20px;">
            <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">
              <div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px; font-weight: 500;">难度选择</div>
                <div style="display: flex; gap: 8px;">
                  <button
                    v-for="d in ['easy', 'medium', 'hard']" :key="d"
                    class="difficulty-btn"
                    :class="{ active: selectedDifficulty === d, ['diff-' + d]: true }"
                    @click="selectedDifficulty = d; loadQuestions()">
                    <i class="fas" :class="d === 'easy' ? 'fa-seedling' : d === 'medium' ? 'fa-fire' : 'fa-bolt'"></i>
                    {{ difficultyLabel(d) }}
                  </button>
                </div>
              </div>
              <div>
                <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px; font-weight: 500;">题型筛选</div>
                <div style="display: flex; gap: 8px;">
                  <button
                    v-for="t in ['choice', 'fill_blank']" :key="t"
                    class="type-btn"
                    :class="{ active: selectedTypes.includes(t) }"
                    @click="toggleType(t)">
                    {{ typeLabel(t) }}
                  </button>
                </div>
              </div>
              <button class="btn btn-primary btn-sm" @click="loadQuestions" style="margin-left:auto;">
                <i class="fas fa-sync-alt"></i> 换一批
              </button>
            </div>
          </div>

          <!-- Loading 状态 - 使用 Semi Design Spin -->
          <div v-if="isLoading" class="card loading-card">
            <div class="loading-container">
              <Spin size="large" />
              <div class="loading-text">{{ loadingMessage }}</div>
              <div class="loading-sub">题目将根据章节知识点智能生成，确保内容准确</div>
            </div>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="errorMessage" class="card" style="text-align:center;padding:40px;">
            <div style="font-size:40px;margin-bottom:16px;opacity:0.3;"><i class="fas fa-exclamation-triangle"></i></div>
            <div style="color:var(--danger);margin-bottom:12px;">{{ errorMessage }}</div>
            <button class="btn btn-primary btn-sm" @click="loadQuestions"><i class="fas fa-redo"></i> 重试</button>
          </div>

          <!-- 题目列表 -->
          <div v-else-if="questions.length > 0" style="display: flex; flex-direction: column; gap: 20px;">
            <div v-for="(q, idx) in questions" :key="q.id" class="card question-card">
              <div style="display:flex;gap:8px;margin-bottom:12px;">
                <span class="question-tag" :class="q.type === 'choice' ? 'choice' : 'fill'">
                  {{ typeLabel(q.type) }}
                </span>
                <span class="question-tag" :class="'diff-tag-' + q.difficulty">
                  {{ difficultyLabel(q.difficulty) }}
                </span>
                <span style="margin-left:auto;font-size:12px;color:var(--text-muted);">{{ q.points }}分</span>
              </div>
              <div class="question-content">{{ idx + 1 }}. {{ q.content }}</div>

              <!-- 选择题 -->
              <div v-if="q.type === 'choice' && q.options" class="options-grid">
                <button v-for="opt in ['A','B','C','D']" :key="opt"
                  class="option-btn" @click="handleSubmit(q.id, opt)">
                  <span class="option-label">{{ opt }}</span>
                  {{ parseOptions(q.options)[opt] }}
                </button>
              </div>

              <!-- 填空题 -->
              <div v-else-if="q.type === 'fill_blank'" class="fill-blank-area">
                <input
                  v-model="fillAnswers[q.id]"
                  class="form-input fill-input"
                  placeholder="请输入答案..."
                  @keyup.enter="handleFillSubmit(q)"
                />
                <button class="btn btn-primary btn-sm" @click="handleFillSubmit(q)">
                  <i class="fas fa-check"></i> 提交
                </button>
              </div>

              <!-- 解答题 -->
              <div v-else>
                <div class="fill-blank-area">
                  <input
                    v-model="fillAnswers[q.id]"
                    class="form-input fill-input"
                    placeholder="请输入答案..."
                    @keyup.enter="handleFillSubmit(q)"
                  />
                  <button class="btn btn-primary btn-sm" @click="handleFillSubmit(q)">
                    <i class="fas fa-check"></i> 提交
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state card">
            <div class="empty-icon"><i class="fas fa-question-circle"></i></div>
            <div class="empty-text">选择难度后点击即可开始练习</div>
          </div>
        </div>

        <div v-else class="empty-state card">
          <div class="empty-icon"><i class="fas fa-hand-pointer"></i></div>
          <div class="empty-text">请从左侧选择一个小节开始刷题</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog-item {
  padding: 6px 8px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  margin-bottom: 2px;
}
.catalog-item:hover {
  background: var(--hover-bg);
  color: var(--text);
}
.catalog-item.active {
  background: var(--primary);
  color: white;
  font-weight: 600;
}

/* 难度按钮 */
.difficulty-btn {
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-card);
  color: var(--text-muted);
  border: 1px solid var(--border);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;
}
.difficulty-btn:hover { border-color: var(--primary); }
.difficulty-btn.active.diff-easy {
  background: rgba(16,185,129,0.15);
  color: #10b981;
  border-color: #10b981;
}
.difficulty-btn.active.diff-medium {
  background: rgba(245,158,11,0.15);
  color: #f59e0b;
  border-color: #f59e0b;
}
.difficulty-btn.active.diff-hard {
  background: rgba(239,68,68,0.15);
  color: #ef4444;
  border-color: #ef4444;
}

/* 题型按钮 */
.type-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-card);
  color: var(--text-muted);
  border: 1px solid var(--border);
  font-family: inherit;
}
.type-btn:hover { border-color: var(--primary); }
.type-btn.active {
  background: rgba(79,70,229,0.15);
  color: var(--primary-light);
  border-color: var(--primary);
}

/* 难度标签 */
.diff-tag-easy {
  background: rgba(16,185,129,0.15) !important;
  color: #10b981 !important;
}
.diff-tag-medium {
  background: rgba(245,158,11,0.15) !important;
  color: #f59e0b !important;
}
.diff-tag-hard {
  background: rgba(239,68,68,0.15) !important;
  color: #ef4444 !important;
}

/* 填空题 */
.question-tag.fill {
  background: rgba(245,158,11,0.15);
  color: #f59e0b;
}

.fill-blank-area {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 8px;
}
.fill-input {
  flex: 1;
  max-width: 400px;
}

/* Loading */
.loading-card {
  padding: 60px 20px;
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.loading-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}
.loading-sub {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
