<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getCourses, getCourseDetail } from '../api/courses'
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

onMounted(loadCourses)
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
      <div style="flex: 1;">
        <div v-if="selectedChapter" class="card" style="margin-bottom: 24px;">
          <h3 style="margin-bottom: 16px; font-weight: 700;">
            正在学习：{{ selectedChapter.title }}
          </h3>
          <div v-if="selectedCourse?.video_url" class="video-player">
            <iframe :src="selectedCourse.video_url" allowfullscreen></iframe>
          </div>
          <div v-else class="empty-state" style="padding: 40px 0;">
            暂无视频资源
          </div>
        </div>

        <div v-else class="empty-state card">
          <div class="empty-icon"><i class="fas fa-hand-pointer"></i></div>
          <div class="empty-text">请从左侧选择一个小节开始学习</div>
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
</style>
