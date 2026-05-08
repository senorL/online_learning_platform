<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getUsers, updateUser, deleteUser, getStats, getChapters, updateChapter, deleteAdminChapter } from '../api/admin'
import { getQuestions, createQuestion, deleteQuestion, importQuestions } from '../api/questions'
import { getCourses, createCourse, deleteCourse } from '../api/courses'

import catalogData from '../assets/catalog.json'

const route = useRoute()
const activeTab = computed(() => route.params.tab || 'questions')

// ---- 题库管理 ----
const questions = ref<any[]>([])
const qPage = ref(1)
const qTotal = ref(0)
const qSearch = ref('')
const qSubject = ref('')
const qDifficulty = ref('')

const showQuestionForm = ref(false)
const newQSubject = ref('数学')
const newQGrade = ref('七年级上册')
const newQChapter = ref('')
const newQSub = ref('')
const newQType = ref('choice')
const newQDifficulty = ref('medium')
const newQContent = ref('')
const newQOptions = ref({ A: '', B: '', C: '', D: '' })
const newQAnswer = ref('A')
const newQPoints = ref(5)
const newQExplanation = ref('')

const qGradeOptions = computed(() => catalogData.find(s => s.title === newQSubject.value)?.children || [])
const qChapterOptions = computed(() => qGradeOptions.value.find(g => g.title === newQGrade.value)?.children || [])
const qSubOptions = computed(() => qChapterOptions.value.find(c => c.title === newQChapter.value)?.children || [])

watch(newQSubject, () => newQGrade.value = qGradeOptions.value[0]?.title || '')
watch(newQGrade, () => newQChapter.value = qChapterOptions.value[0]?.title || '')
watch(newQChapter, () => newQSub.value = qSubOptions.value[0]?.title || '')

const difficultyLabel = (d: string) => {
  if (d === 'easy') return '简单'
  if (d === 'hard') return '困难'
  return '中等'
}
const difficultyClass = (d: string) => {
  if (d === 'easy') return 'badge-active'
  if (d === 'hard') return 'badge-admin'
  return 'badge-teacher'
}

const handleCreateQuestion = async () => {
  if (!newQChapter.value) return alert('请选择章节')
  if (!newQContent.value) return alert('请输入题干')
  
  const chapterName = newQSub.value ? `${newQChapter.value} - ${newQSub.value}` : newQChapter.value
  const data: any = {
    subject: newQSubject.value,
    chapter: chapterName,
    type: newQType.value,
    difficulty: newQDifficulty.value,
    content: newQContent.value,
    answer: newQAnswer.value,
    points: newQPoints.value,
    explanation: newQExplanation.value,
  }
  if (newQType.value === 'choice') {
    data.options = JSON.stringify(newQOptions.value)
  }
  await createQuestion(data)
  showQuestionForm.value = false
  newQContent.value = ''
  loadQuestions()
}

const loadQuestions = async () => {
  const res = await getQuestions({
    page: qPage.value, page_size: 20,
    subject: qSubject.value || undefined,
    keyword: qSearch.value || undefined,
    difficulty: qDifficulty.value || undefined,
  })
  if (res.data.code === 200) {
    questions.value = res.data.data.items
    qTotal.value = res.data.data.total
  }
}

const handleDeleteQ = async (id: number) => {
  if (!confirm('确定删除这道题目？')) return
  await deleteQuestion(id)
  loadQuestions()
}

// ---- 课程管理 ----
const coursesList = ref<any[]>([])
const showCourseForm = ref(false)

const newCourseSubject = ref('数学')
const newCourseGrade = ref('七年级上册')
const newCourseChapter = ref('')
const newCourseSub = ref('')
const newCourseDesc = ref('')
const newCourseVideo = ref('')

const courseGradeOptions = computed(() => catalogData.find(s => s.title === newCourseSubject.value)?.children || [])
const courseChapterOptions = computed(() => courseGradeOptions.value.find(g => g.title === newCourseGrade.value)?.children || [])
const courseSubOptions = computed(() => courseChapterOptions.value.find(c => c.title === newCourseChapter.value)?.children || [])

watch(newCourseSubject, () => newCourseGrade.value = courseGradeOptions.value[0]?.title || '')
watch(newCourseGrade, () => newCourseChapter.value = courseChapterOptions.value[0]?.title || '')
watch(newCourseChapter, () => newCourseSub.value = courseSubOptions.value[0]?.title || '')

const loadCourses = async () => {
  const res = await getCourses()
  if (res.data.code === 200) coursesList.value = res.data.data
}

const handleCreateCourse = async () => {
  if (!newCourseChapter.value) return alert('请选择章节')
  const name = newCourseSub.value ? `${newCourseChapter.value} - ${newCourseSub.value}` : newCourseChapter.value
  
  await createCourse({
    name,
    subject: newCourseSubject.value,
    grade: newCourseGrade.value,
    description: newCourseDesc.value,
    video_url: newCourseVideo.value
  })
  showCourseForm.value = false
  newCourseDesc.value = ''
  newCourseVideo.value = ''
  loadCourses()
}

const handleDeleteCourse = async (id: number) => {
  if (!confirm('确定删除这门课程？')) return
  await deleteCourse(id)
  loadCourses()
}

// ---- 章节管理 ----
const chaptersList = ref<any[]>([])
const chPage = ref(1)
const chTotal = ref(0)
const chSearch = ref('')
const chSubject = ref('')
const editingChapter = ref<any>(null)
const editChapterTitle = ref('')
const editChapterOrder = ref(0)

const loadChapters = async () => {
  const res = await getChapters({
    page: chPage.value, page_size: 20,
    keyword: chSearch.value || undefined,
    subject: chSubject.value || undefined,
  })
  if (res.data.code === 200) {
    chaptersList.value = res.data.data.items
    chTotal.value = res.data.data.total
  }
}

const startEditChapter = (ch: any) => {
  editingChapter.value = ch
  editChapterTitle.value = ch.title
  editChapterOrder.value = ch.sort_order
}

const saveEditChapter = async () => {
  if (!editingChapter.value) return
  await updateChapter(editingChapter.value.id, {
    title: editChapterTitle.value,
    sort_order: editChapterOrder.value,
  })
  editingChapter.value = null
  loadChapters()
}

const handleDeleteChapter = async (id: number) => {
  if (!confirm('确定删除此章节及其所有视频？')) return
  await deleteAdminChapter(id)
  loadChapters()
}

// ---- 用户管理 ----
const users = ref<any[]>([])
const uSearch = ref('')
const uPage = ref(1)
const uTotal = ref(0)

const loadUsers = async () => {
  const res = await getUsers({ page: uPage.value, page_size: 20, keyword: uSearch.value || undefined })
  if (res.data.code === 200) {
    users.value = res.data.data.items
    uTotal.value = res.data.data.total
  }
}

const toggleActive = async (u: any) => {
  await updateUser(u.id, { is_active: !u.is_active })
  loadUsers()
}

const changeRole = async (u: any, role: string) => {
  await updateUser(u.id, { role })
  loadUsers()
}

const handleDeleteUser = async (u: any) => {
  if (u.role === 'admin') {
    alert('不能删除管理员账号')
    return
  }
  if (!confirm(`确定要永久删除用户 "${u.username}" 及其所有数据吗？此操作不可恢复！`)) return
  await deleteUser(u.id)
  loadUsers()
}

const editingUser = ref<any>(null)
const editUserForm = ref({ username: '', password: '' })

const startEditUser = (u: any) => {
  editingUser.value = u
  editUserForm.value = { username: u.username, password: '' }
}

const saveEditUser = async () => {
  if (!editingUser.value) return
  if (editUserForm.value.username.length < 2) return alert('用户名至少2个字符')
  if (editUserForm.value.password && editUserForm.value.password.length < 6) return alert('密码至少6位')
  
  const payload: any = { username: editUserForm.value.username }
  if (editUserForm.value.password) {
    payload.password = editUserForm.value.password
  }
  
  await updateUser(editingUser.value.id, payload)
  editingUser.value = null
  loadUsers()
}

// ---- 数据统计 ----
const stats = ref<any>({})

const loadStats = async () => {
  const res = await getStats()
  if (res.data.code === 200) stats.value = res.data.data
}

const loadData = () => {
  const tab = activeTab.value
  if (tab === 'questions') loadQuestions()
  else if (tab === 'courses') loadCourses()
  else if (tab === 'chapters') loadChapters()
  else if (tab === 'users') loadUsers()
  else if (tab === 'stats') loadStats()
}

watch(activeTab, loadData)
onMounted(loadData)
</script>

<template>
  <div class="fade-in">

    <!-- 题库管理 -->
    <div v-if="activeTab === 'questions'">
      <div style="margin-bottom:16px;display:flex;gap:10px;">
        <button class="btn btn-primary btn-sm" @click="showQuestionForm = !showQuestionForm">
          <i class="fas fa-plus"></i> 新增题目
        </button>
      </div>

      <div v-if="showQuestionForm" class="card" style="margin-bottom:20px;">
        <div class="grid-2">
          <div class="form-group">
            <label>学科</label>
            <select v-model="newQSubject" class="form-select">
              <option v-for="s in catalogData" :key="s.title" :value="s.title">{{ s.title }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>年级</label>
            <select v-model="newQGrade" class="form-select">
              <option v-for="g in qGradeOptions" :key="g.title" :value="g.title">{{ g.title }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>章节</label>
            <select v-model="newQChapter" class="form-select">
              <option v-for="c in qChapterOptions" :key="c.title" :value="c.title">{{ c.title }}</option>
            </select>
          </div>
          <div class="form-group" v-if="qSubOptions.length > 0">
            <label>小节</label>
            <select v-model="newQSub" class="form-select">
              <option value="">(无)</option>
              <option v-for="sub in qSubOptions" :key="sub.title" :value="sub.title">{{ sub.title }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>题型</label>
            <select v-model="newQType" class="form-select">
              <option value="choice">选择题</option>
              <option value="fill_blank">填空题</option>
              <option value="essay">解答题</option>
            </select>
          </div>
          <div class="form-group">
            <label>难度</label>
            <select v-model="newQDifficulty" class="form-select">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
          <div class="form-group">
            <label>分值</label>
            <input v-model="newQPoints" type="number" class="form-input" />
          </div>
        </div>

        <div class="form-group" style="margin-top:12px;">
          <label>题干</label>
          <textarea v-model="newQContent" class="form-input" rows="3"></textarea>
        </div>

        <div v-if="newQType === 'choice'" class="grid-2" style="margin-top:12px;">
          <div class="form-group"><label>A</label><input v-model="newQOptions.A" class="form-input" /></div>
          <div class="form-group"><label>B</label><input v-model="newQOptions.B" class="form-input" /></div>
          <div class="form-group"><label>C</label><input v-model="newQOptions.C" class="form-input" /></div>
          <div class="form-group"><label>D</label><input v-model="newQOptions.D" class="form-input" /></div>
          <div class="form-group">
            <label>正确答案</label>
            <select v-model="newQAnswer" class="form-select">
              <option value="A">A</option><option value="B">B</option><option value="C">C</option><option value="D">D</option>
            </select>
          </div>
        </div>

        <div v-else class="form-group" style="margin-top:12px;">
          <label>正确答案</label>
          <textarea v-model="newQAnswer" class="form-input" rows="2"></textarea>
        </div>

        <div class="form-group" style="margin-top:12px;">
          <label>解析</label>
          <textarea v-model="newQExplanation" class="form-input" rows="2"></textarea>
        </div>
        
        <button class="btn btn-primary btn-sm" @click="handleCreateQuestion" style="margin-top:12px;"><i class="fas fa-save"></i> 保存题目</button>
      </div>

      <div class="search-box">
        <input v-model="qSearch" class="search-input" placeholder="搜索题目关键词..." @keyup.enter="loadQuestions" />
        <select v-model="qSubject" class="form-select" style="width:140px;" @change="loadQuestions">
          <option value="">全部学科</option>
          <option v-for="s in ['数学','语文','英语','物理','化学','生物','地理','道德与法治']" :value="s">{{ s }}</option>
        </select>
        <select v-model="qDifficulty" class="form-select" style="width:120px;" @change="loadQuestions">
          <option value="">全部难度</option>
          <option value="easy">简单</option>
          <option value="medium">中等</option>
          <option value="hard">困难</option>
        </select>
        <button class="btn btn-primary btn-sm" @click="loadQuestions"><i class="fas fa-search"></i></button>
      </div>
      <div style="margin-bottom:12px;color:var(--text-muted);font-size:13px;">共 {{ qTotal }} 道题目</div>

      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>学科</th><th>题型</th><th>难度</th><th>来源</th><th>题目</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="q in questions" :key="q.id">
            <td>{{ q.id }}</td>
            <td><span class="badge badge-student">{{ q.subject }}</span></td>
            <td>{{ q.type === 'choice' ? '选择' : (q.type === 'fill_blank' ? '填空' : '解答') }}</td>
            <td><span class="badge" :class="difficultyClass(q.difficulty)">{{ difficultyLabel(q.difficulty) }}</span></td>
            <td><span style="font-size:12px;color:var(--text-muted)">{{ q.source === 'ai' ? 'AI' : '手动' }}</span></td>
            <td style="max-width:350px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ q.content }}</td>
            <td><button class="btn btn-sm btn-danger" @click="handleDeleteQ(q.id)"><i class="fas fa-trash"></i></button></td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button class="page-btn" :disabled="qPage <= 1" @click="qPage--; loadQuestions()">上一页</button>
        <span style="padding:8px 12px;color:var(--text-muted);font-size:13px;">第 {{ qPage }} 页</span>
        <button class="page-btn" :disabled="questions.length < 20" @click="qPage++; loadQuestions()">下一页</button>
      </div>
    </div>

    <!-- 课程管理 -->
    <div v-if="activeTab === 'courses'">
      <div style="margin-bottom:16px;">
        <button class="btn btn-primary btn-sm" @click="showCourseForm = !showCourseForm">
          <i class="fas fa-plus"></i> 新增课程
        </button>
      </div>

      <div v-if="showCourseForm" class="card" style="margin-bottom:20px;">
        <div class="grid-2">
          <div class="form-group">
            <label>学科</label>
            <select v-model="newCourseSubject" class="form-select">
              <option v-for="s in catalogData" :key="s.title" :value="s.title">{{ s.title }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>年级</label>
            <select v-model="newCourseGrade" class="form-select">
              <option v-for="g in courseGradeOptions" :key="g.title" :value="g.title">{{ g.title }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>章节</label>
            <select v-model="newCourseChapter" class="form-select">
              <option v-for="c in courseChapterOptions" :key="c.title" :value="c.title">{{ c.title }}</option>
            </select>
          </div>
          <div class="form-group" v-if="courseSubOptions.length > 0">
            <label>小节</label>
            <select v-model="newCourseSub" class="form-select">
              <option value="">(无)</option>
              <option v-for="sub in courseSubOptions" :key="sub.title" :value="sub.title">{{ sub.title }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="newCourseDesc" class="form-input" placeholder="课程描述" />
          </div>
          <div class="form-group">
            <label>视频链接</label>
            <input v-model="newCourseVideo" class="form-input" placeholder="视频外部链接（如 B站等 iframe src）" />
          </div>
        </div>
        <button class="btn btn-primary btn-sm" @click="handleCreateCourse"><i class="fas fa-save"></i> 保存</button>
      </div>

      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>课程名</th><th>学科</th><th>年级</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in coursesList" :key="c.id">
            <td>{{ c.id }}</td>
            <td>{{ c.name }}</td>
            <td><span class="badge badge-student">{{ c.subject }}</span></td>
            <td>{{ c.grade || '-' }}</td>
            <td><button class="btn btn-sm btn-danger" @click="handleDeleteCourse(c.id)"><i class="fas fa-trash"></i></button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 章节管理 -->
    <div v-if="activeTab === 'chapters'">
      <div class="search-box">
        <input v-model="chSearch" class="search-input" placeholder="搜索章节名称..." @keyup.enter="loadChapters" />
        <select v-model="chSubject" class="form-select" style="width:140px;" @change="loadChapters">
          <option value="">全部学科</option>
          <option v-for="s in ['数学','语文','英语','物理','化学','生物','地理','道德与法治']" :value="s">{{ s }}</option>
        </select>
        <button class="btn btn-primary btn-sm" @click="loadChapters"><i class="fas fa-search"></i></button>
      </div>
      <div style="margin-bottom:12px;color:var(--text-muted);font-size:13px;">共 {{ chTotal }} 个章节</div>

      <!-- 编辑弹窗 -->
      <div v-if="editingChapter" class="modal-overlay" @click.self="editingChapter = null">
        <div class="modal-content" style="position:relative;">
          <h3 style="margin-bottom:20px;font-weight:700;">编辑章节</h3>
          <div class="form-group">
            <label>章节标题</label>
            <input v-model="editChapterTitle" class="form-input" />
          </div>
          <div class="form-group">
            <label>排序序号</label>
            <input v-model.number="editChapterOrder" type="number" class="form-input" />
          </div>
          <div style="display:flex;gap:10px;margin-top:16px;">
            <button class="btn btn-primary btn-sm" @click="saveEditChapter"><i class="fas fa-save"></i> 保存</button>
            <button class="btn btn-ghost btn-sm" @click="editingChapter = null">取消</button>
          </div>
        </div>
      </div>

      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>章节名称</th><th>所属课程</th><th>学科</th><th>年级</th><th>视频数</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="ch in chaptersList" :key="ch.id">
            <td>{{ ch.id }}</td>
            <td style="font-weight:500;">{{ ch.title }}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ ch.course_name }}</td>
            <td><span class="badge badge-student">{{ ch.course_subject }}</span></td>
            <td>{{ ch.course_grade || '-' }}</td>
            <td>{{ ch.video_count }}</td>
            <td style="display:flex;gap:6px;">
              <button class="btn btn-sm btn-ghost" @click="startEditChapter(ch)"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-danger" @click="handleDeleteChapter(ch.id)"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button class="page-btn" :disabled="chPage <= 1" @click="chPage--; loadChapters()">上一页</button>
        <span style="padding:8px 12px;color:var(--text-muted);font-size:13px;">第 {{ chPage }} 页</span>
        <button class="page-btn" :disabled="chaptersList.length < 20" @click="chPage++; loadChapters()">下一页</button>
      </div>
    </div>

    <!-- 用户管理 -->
    <div v-if="activeTab === 'users'">
      <div class="search-box">
        <input v-model="uSearch" class="search-input" placeholder="搜索用户名..." @keyup.enter="loadUsers" />
        <button class="btn btn-primary btn-sm" @click="loadUsers"><i class="fas fa-search"></i></button>
      </div>

      <!-- 编辑用户弹窗 -->
      <div v-if="editingUser" class="modal-overlay" @click.self="editingUser = null">
        <div class="modal-content" style="position:relative;">
          <h3 style="margin-bottom:20px;font-weight:700;">修改用户信息</h3>
          <div class="form-group">
            <label>用户名</label>
            <input v-model="editUserForm.username" class="form-input" placeholder="请输入新用户名" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="editUserForm.password" type="password" class="form-input" placeholder="留空表示不修改密码" />
          </div>
          <div style="display:flex;gap:10px;margin-top:16px;">
            <button class="btn btn-primary btn-sm" @click="saveEditUser"><i class="fas fa-save"></i> 保存</button>
            <button class="btn btn-ghost btn-sm" @click="editingUser = null">取消</button>
          </div>
        </div>
      </div>

      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>用户名</th><th>角色</th><th>年级</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>
              <span class="badge" :class="{'badge-admin': u.role==='admin', 'badge-student': u.role==='student'}">
                {{ u.role === 'admin' ? '管理员' : '学生' }}
              </span>
            </td>
            <td>{{ u.grade || '-' }}</td>
            <td>
              <span class="badge" :class="u.is_active ? 'badge-active' : 'badge-inactive'">
                {{ u.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td style="display:flex;gap:6px;">
              <button class="btn btn-sm btn-ghost" @click="startEditUser(u)" title="编辑用户"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-ghost" @click="toggleActive(u)">
                {{ u.is_active ? '禁用' : '启用' }}
              </button>
              <select @change="changeRole(u, ($event.target as HTMLSelectElement).value)"
                class="form-select" style="width:90px;padding:6px;">
                <option value="student" :selected="u.role==='student'">学生</option>
                <option value="admin" :selected="u.role==='admin'">管理员</option>
              </select>
              <button class="btn btn-sm btn-danger" @click="handleDeleteUser(u)" title="删除用户"><i class="fas fa-trash"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 数据统计 -->
    <div v-if="activeTab === 'stats'">
      <div class="grid-3" style="margin-bottom:32px;">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_students || 0 }}</div>
          <div class="stat-label">注册学生数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_questions || 0 }}</div>
          <div class="stat-label">题库总题数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.daily_active || 0 }}</div>
          <div class="stat-label">今日活跃</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <h4 style="margin-bottom:16px;font-weight:700;">近30天每日答题量</h4>
          <div v-for="d in (stats.daily_counts || [])" :key="d.date" style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:12px;color:var(--text-muted);width:80px;">{{ d.date.slice(5) }}</span>
            <div style="flex:1;height:20px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
              <div :style="{width: Math.min(d.count * 5, 100) + '%', height: '100%', background: 'linear-gradient(90deg, var(--primary), var(--accent))', borderRadius: '4px'}"></div>
            </div>
            <span style="font-size:12px;color:var(--text-muted);width:30px;text-align:right;">{{ d.count }}</span>
          </div>
        </div>
        <div class="card">
          <h4 style="margin-bottom:16px;font-weight:700;">各学科题目分布</h4>
          <div v-for="s in (stats.subject_distribution || [])" :key="s.subject"
            style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <span style="font-size:13px;width:50px;">{{ s.subject }}</span>
            <div style="flex:1;height:24px;background:rgba(255,255,255,0.05);border-radius:6px;overflow:hidden;">
              <div :style="{width: Math.min(s.count * 2, 100) + '%', height: '100%', background: 'linear-gradient(90deg, var(--primary), var(--accent))', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: '8px'}">
                <span style="font-size:11px;font-weight:600;">{{ s.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
