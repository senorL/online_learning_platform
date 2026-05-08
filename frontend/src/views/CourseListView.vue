<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getCourses, getCourseDetail } from '../api/courses'
import { recordProcess, getLatestProcess } from '../api/process'
import catalogData from '../assets/catalog.json'

const userGrade = localStorage.getItem('grade') || '七年级'
const subjects = computed(() => {
  if (userGrade === '七年级') return ['数学', '语文', '英语', '道德与法治', '生物', '地理']
  if (userGrade === '八年级') return ['数学', '语文', '英语', '道德与法治', '物理', '生物', '地理']
  return ['数学', '语文', '英语', '道德与法治', '物理', '化学', '生物', '地理']
})
const currentSubject = ref('数学')
const courses = ref<any[]>([])
const selectedCourse = ref<any>(null)
const selectedChapter = ref<any>(null)
const processMinute = ref(0)
const processSecond = ref(0)
const processMessage = ref('')
const processSaving = ref(false)

// 进度提醒横幅
const latestProcess = ref<any>(null)
const showBanner = ref(false)

const defaultVideos: Record<string, string> = {
  '数学': '//player.bilibili.com/player.html?bvid=BV1qE411H7Uv',
  '物理': '//player.bilibili.com/player.html?bvid=BV1Mb421n7nB',
  '化学': '//player.bilibili.com/player.html?bvid=BV1wb411x78e',
  '地理': '//player.bilibili.com/player.html?bvid=BV1ni4y1u7qn',
  '生物': '//player.bilibili.com/player.html?bvid=BV1n94y1g7XG',
  '英语': '//player.bilibili.com/player.html?bvid=BV1wt411G7QY',
  '道德与法治': '//player.bilibili.com/player.html?bvid=BV1K4KyzNEVJ',
  '语文': '//player.bilibili.com/player.html?bvid=BV1jc411c7CS'
}

const courseDetailsCache = ref<Record<number, any>>({})

const currentCatalog = computed(() => {
  return catalogData.find((s: any) => s.title === currentSubject.value) || null
})

const loadCourses = async () => {
  const res = await getCourses({ subject: currentSubject.value })
  if (res.data.code === 200) courses.value = res.data.data
}

const selectSubject = (s: string) => {
  currentSubject.value = s
  selectedCourse.value = null
  selectedChapter.value = null
  loadCourses()
}

const formatVideoUrl = (url: string) => {
  if (!url) return '';
  if (url.includes('bilibili.com/video/')) {
    const bvidMatch = url.match(/video\/(BV\w+)/);
    const pMatch = url.match(/[?&]p=(\d+)/);
    if (bvidMatch) {
      let playerUrl = `//player.bilibili.com/player.html?bvid=${bvidMatch[1]}`;
      if (pMatch) {
        playerUrl += `&page=${pMatch[1]}`;
      }
      return playerUrl;
    }
  }
  return url;
}

const selectSubChapter = async (subChapter: any, gradeTitle: string, chapterTitle: string) => {
  selectedChapter.value = subChapter
  
  const customCourseName = (subChapter.title === chapterTitle) ? chapterTitle : `${chapterTitle} - ${subChapter.title}`
  const customCourse = courses.value.find(c => c.name === customCourseName && c.video_url)
  
  let videoUrl = defaultVideos[currentSubject.value] || ''

  if (customCourse && customCourse.video_url) {
    videoUrl = customCourse.video_url
  } else {
    const basicCourse = courses.value.find(c => c.grade === gradeTitle || c.name.includes(gradeTitle))
    if (basicCourse) {
      let fullCourse = courseDetailsCache.value[basicCourse.id]
      if (!fullCourse) {
        const res = await getCourseDetail(basicCourse.id)
        if (res.data.code === 200) {
          fullCourse = res.data.data
          courseDetailsCache.value[basicCourse.id] = fullCourse
        }
      }

      if (fullCourse && fullCourse.chapters) {
        const matchedChapter = fullCourse.chapters.find((c: any) => c.title === subChapter.title)
        if (matchedChapter && matchedChapter.videos && matchedChapter.videos.length > 0) {
          videoUrl = matchedChapter.videos[0].url
        }
      }
    }
  }

  selectedCourse.value = { video_url: formatVideoUrl(videoUrl) }
}

const saveProcess = async () => {
  if (!selectedChapter.value) return
  processSaving.value = true
  try {
    const res = await recordProcess({
      subject: currentSubject.value,
      chapter: selectedChapter.value.title,
      minute: processMinute.value,
      second: processSecond.value
    })
    if (res.data.code === 200) {
      processMessage.value = 'success'
      // 保存成功后刷新横幅数据
      await loadLatestProcess()
      setTimeout(() => processMessage.value = '', 3000)
    } else {
      processMessage.value = 'error'
      setTimeout(() => processMessage.value = '', 3000)
    }
  } catch (err) {
    processMessage.value = 'error'
    setTimeout(() => processMessage.value = '', 3000)
  } finally {
    processSaving.value = false
  }
}

const loadLatestProcess = async () => {
  try {
    const res = await getLatestProcess()
    if (res.data.code === 200 && res.data.data) {
      latestProcess.value = res.data.data
      showBanner.value = true
    }
  } catch (e) {
    // 静默处理
  }
}

// 点击横幅跳转到对应章节
const jumpToChapter = () => {
  if (!latestProcess.value) return
  const targetSubject = latestProcess.value.subject
  const targetChapter = latestProcess.value.chapter

  // 切换学科
  currentSubject.value = targetSubject
  loadCourses()

  // 在目录中查找并展开对应章节
  const catalog = catalogData.find((s: any) => s.title === targetSubject)
  if (catalog) {
    for (const grade of (catalog as any).children || []) {
      for (const chapter of grade.children || []) {
        if (chapter.children && chapter.children.length > 0) {
          for (const sub of chapter.children) {
            if (sub.title === targetChapter) {
              selectSubChapter(sub, grade.title, chapter.title)
              showBanner.value = false
              return
            }
          }
        } else {
          if (chapter.title === targetChapter) {
            selectSubChapter(chapter, grade.title, chapter.title)
            showBanner.value = false
            return
          }
        }
      }
    }
  }

  // 即使没找到精确匹配也关闭横幅
  showBanner.value = false
}

const dismissBanner = () => {
  showBanner.value = false
}

onMounted(async () => {
  await loadCourses()
  await loadLatestProcess()
})
</script>

<template>
  <div class="fade-in">
    <!-- 学习进度提醒横幅 -->
    <div v-if="showBanner && latestProcess" class="process-banner">
      <div class="banner-content">
        <div class="banner-icon">
          <i class="fas fa-history"></i>
        </div>
        <div class="banner-text">
          <span class="banner-label">上次学到</span>
          <span class="banner-subject">{{ latestProcess.subject }}</span>
          <span class="banner-separator">·</span>
          <span class="banner-chapter">{{ latestProcess.chapter }}</span>
          <span class="banner-time">（{{ latestProcess.minute }}分{{ latestProcess.second }}秒）</span>
        </div>
        <button class="banner-btn" @click="jumpToChapter">
          <i class="fas fa-play-circle"></i> 继续学习
        </button>
        <button class="banner-close" @click="dismissBanner">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- 学科选择 -->
    <div class="filter-tabs">
      <button v-for="s in subjects" :key="s"
        class="filter-tab" :class="{ active: currentSubject === s }"
        @click="selectSubject(s)">{{ s }}</button>
    </div>

    <div class="course-layout">
      <!-- 左侧目录树 -->
      <div class="card catalog-panel">
        <h4 class="catalog-header">
          <i class="fas fa-list-ul"></i> {{ currentSubject }} 目录
        </h4>
        <div v-if="currentCatalog" class="catalog-tree">
          <div v-for="(grade, gIdx) in currentCatalog.children" :key="gIdx" class="catalog-grade">
            <div class="grade-title">
              {{ grade.title }}
            </div>
            <div v-for="(chapter, cIdx) in grade.children" :key="cIdx" class="catalog-chapter">
              <template v-if="chapter.children && chapter.children.length > 0">
                <div class="chapter-title">{{ chapter.title }}</div>
                <div class="chapter-children">
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
                  @click="selectSubChapter(chapter, grade.title, chapter.title)">
                  {{ chapter.title }}
                </div>
              </template>
            </div>
          </div>
        </div>
        <div v-else class="empty-state" style="padding: 20px 0;">暂无目录数据</div>
      </div>

      <!-- 右侧内容区 -->
      <div class="content-panel">
        <div v-if="selectedChapter" class="card" style="margin-bottom: 24px;">
          <h3 class="video-title">
            <i class="fas fa-play-circle" style="color: var(--primary); margin-right: 8px;"></i>
            正在学习：{{ selectedChapter.title }}
          </h3>
          <div v-if="selectedCourse?.video_url" class="video-player">
            <iframe :src="selectedCourse.video_url" allowfullscreen></iframe>
          </div>
          <div v-else class="empty-state" style="padding: 40px 0;">
            暂无视频资源
          </div>

          <!-- ★ 记录学习进度组件 ★ -->
          <div class="progress-recorder">
            <div class="recorder-header">
              <div class="recorder-icon">
                <i class="fas fa-bookmark"></i>
              </div>
              <div class="recorder-title">记录学习进度</div>
              <div class="recorder-subtitle">保存当前视频观看位置，下次可快速回到这里</div>
            </div>
            <div class="recorder-controls">
              <div class="time-input-group">
                <div class="time-input-wrapper">
                  <input type="number" v-model="processMinute" min="0" class="time-input" placeholder="0" />
                  <span class="time-label">分</span>
                </div>
                <span class="time-colon">:</span>
                <div class="time-input-wrapper">
                  <input type="number" v-model="processSecond" min="0" max="59" class="time-input" placeholder="0" />
                  <span class="time-label">秒</span>
                </div>
              </div>
              <button class="btn btn-primary recorder-save-btn" @click="saveProcess" :disabled="processSaving">
                <i class="fas fa-save" style="margin-right: 4px;"></i>
                {{ processSaving ? '保存中...' : '保存进度' }}
              </button>
              <transition name="msg-fade">
                <div v-if="processMessage === 'success'" class="recorder-msg success">
                  <i class="fas fa-check-circle"></i> 进度已保存
                </div>
                <div v-else-if="processMessage === 'error'" class="recorder-msg error">
                  <i class="fas fa-exclamation-circle"></i> 保存失败，请重试
                </div>
              </transition>
            </div>
          </div>
        </div>

        <div v-else class="empty-state card empty-placeholder">
          <div class="empty-icon"><i class="fas fa-hand-pointer"></i></div>
          <div class="empty-text">请从左侧目录选择一个小节开始学习</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== 进度提醒横幅 ===== */
.process-banner {
  margin-bottom: 20px;
  background: linear-gradient(135deg, rgba(51, 112, 255, 0.12), rgba(20, 201, 201, 0.08));
  border: 1px solid rgba(51, 112, 255, 0.25);
  border-radius: var(--radius);
  overflow: hidden;
  animation: bannerSlideIn 0.4s ease-out;
}

@keyframes bannerSlideIn {
  from { opacity: 0; transform: translateY(-12px); }
  to { opacity: 1; transform: translateY(0); }
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 20px;
}

.banner-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.banner-text {
  flex: 1;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 14px;
  color: var(--text);
}

.banner-label {
  font-weight: 500;
  color: var(--text-muted);
}

.banner-subject {
  font-weight: 700;
  color: var(--primary);
  background: var(--semi-color-primary-bg);
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 13px;
}

.banner-separator {
  color: var(--text-muted);
}

.banner-chapter {
  font-weight: 600;
  color: var(--text);
}

.banner-time {
  color: var(--text-muted);
  font-size: 13px;
}

.banner-btn {
  flex-shrink: 0;
  padding: 8px 18px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.banner-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(51, 112, 255, 0.3);
}

.banner-close {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-xs);
  transition: all 0.2s;
}

.banner-close:hover {
  background: var(--hover-bg);
  color: var(--text);
}

/* ===== 课程布局 ===== */
.course-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  margin-top: 20px;
}

.catalog-panel {
  width: 320px;
  padding: 16px;
  flex-shrink: 0;
  max-height: 80vh;
  overflow-y: auto;
}

.content-panel {
  flex: 1;
  min-width: 0;
}

.catalog-header {
  margin-bottom: 16px;
  font-weight: 700;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}

.catalog-tree {
  /* nothing extra */
}

.catalog-grade {
  margin-bottom: 12px;
}

.grade-title {
  font-weight: 600;
  color: var(--primary-light);
  margin-bottom: 8px;
}

.catalog-chapter {
  margin-left: 12px;
  margin-bottom: 8px;
}

.chapter-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}

.chapter-children {
  margin-left: 12px;
}

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

.video-title {
  margin-bottom: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
}

.empty-placeholder {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* ===== 记录学习进度组件 ===== */
.progress-recorder {
  margin-top: 20px;
  padding: 20px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s;
}

.progress-recorder:hover {
  border-color: rgba(51, 112, 255, 0.3);
}

.recorder-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.recorder-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: var(--semi-color-primary-bg);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}

.recorder-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.recorder-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  flex-basis: 100%;
  margin-left: 46px;
  margin-top: -6px;
}

.recorder-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.time-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  transition: all 0.2s;
}

.time-input-group:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(51, 112, 255, 0.15);
}

.time-input-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.time-input {
  width: 52px;
  padding: 6px 8px;
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 16px;
  font-weight: 600;
  text-align: center;
  outline: none;
  font-family: 'Inter', monospace;
  -moz-appearance: textfield;
}

.time-input::-webkit-outer-spin-button,
.time-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.time-label {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.time-colon {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-muted);
}

.recorder-save-btn {
  padding: 8px 20px;
  font-size: 13px;
}

.recorder-save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.recorder-msg {
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-xs);
}

.recorder-msg.success {
  color: var(--success);
  background: rgba(27, 191, 108, 0.1);
}

.recorder-msg.error {
  color: var(--danger);
  background: rgba(245, 74, 69, 0.1);
}

/* 消息淡入淡出动画 */
.msg-fade-enter-active {
  animation: msgIn 0.3s ease-out;
}
.msg-fade-leave-active {
  animation: msgIn 0.2s ease-in reverse;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
