<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getHeatmap, getActivity } from '../api/auth'

const heatmap = ref<Record<string, number>>({})
const selectedDate = ref('')
const dailyDetails = ref<any[]>([])
const loadingDetails = ref(false)

const subjectIcons: Record<string, string> = {
  '数学': 'fa-calculator',
  '语文': 'fa-book',
  '英语': 'fa-language',
  '道德与法治': 'fa-balance-scale',
  '物理': 'fa-atom',
  '化学': 'fa-flask',
  '生物': 'fa-leaf',
  '地理': 'fa-globe-asia'
}

const loadHeatmap = async () => {
  const res = await getHeatmap()
  if (res.data.code === 200) heatmap.value = res.data.data
}

const getDayStr = (day: number): string => {
  const d = new Date()
  d.setDate(d.getDate() - (371 - day))
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

const getHeatLevel = (day: number): string => {
  const c = heatmap.value[getDayStr(day)] || 0
  if (c === 0) return 'heat-0'
  if (c < 3) return 'heat-1'
  if (c < 5) return 'heat-2'
  if (c < 7) return 'heat-3'
  if (c < 10) return 'heat-4'
  return 'heat-5'
}

const totalDays = ref(Object.keys(heatmap.value).length)
const totalCount = ref(0)

const handleCellClick = async (day: number) => {
  const dateStr = getDayStr(day)
  if (!heatmap.value[dateStr]) return
  
  selectedDate.value = dateStr
  loadingDetails.value = true
  try {
    const res = await getActivity(dateStr)
    if (res.data.code === 200) {
      dailyDetails.value = res.data.data
    }
  } finally {
    loadingDetails.value = false
  }
}

onMounted(async () => {
  await loadHeatmap()
  totalDays.value = Object.keys(heatmap.value).length
  totalCount.value = Object.values(heatmap.value).reduce((a, b) => a + b, 0)
})
</script>

<template>
  <div class="fade-in">
    <div class="card" style="text-align:center;padding:40px;">
      <h3 style="font-size:22px;font-weight:800;margin-bottom:32px;">
        <i class="fas fa-fire" style="color:#f59e0b;margin-right:8px;"></i>学习成就热力图
      </h3>

      <div class="grid-3" style="max-width:400px;margin:0 auto 32px;">
        <div class="stat-card">
          <div class="stat-value">{{ totalDays }}</div>
          <div class="stat-label">活跃天数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalCount }}</div>
          <div class="stat-label">总做题数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ Math.max(...Object.values(heatmap), 0) }}</div>
          <div class="stat-label">单日最高</div>
        </div>
      </div>

      <div class="heatmap-container" style="overflow-x:auto;padding:16px;">
        <div class="heatmap-grid">
          <div v-for="day in 371" :key="day"
            class="heatmap-cell" 
            :class="[getHeatLevel(day), { 'clickable': heatmap[getDayStr(day)] > 0, 'selected-cell': selectedDate === getDayStr(day) }]"
            :title="`${getDayStr(day)}: ${heatmap[getDayStr(day)] || 0}题`"
            @click="handleCellClick(day)">
          </div>
        </div>
      </div>

      <div class="heatmap-legend">
        <span>少</span>
        <div class="heatmap-cell heat-0"></div>
        <div class="heatmap-cell heat-1"></div>
        <div class="heatmap-cell heat-2"></div>
        <div class="heatmap-cell heat-3"></div>
        <div class="heatmap-cell heat-4"></div>
        <div class="heatmap-cell heat-5"></div>
        <span>多</span>
      </div>

      <p style="margin-top:24px;color:var(--text-muted);font-size:14px;">
        颜色越深代表当日做题量越多，点击有颜色的格子查看详情！
      </p>

      <div v-if="selectedDate" class="daily-details fade-in" style="margin-top: 32px;text-align:left;max-width:600px;margin-left:auto;margin-right:auto;">
        <h4 style="margin-bottom:16px;font-weight:700;"><i class="fas fa-calendar-day" style="color:var(--primary);margin-right:8px;"></i>{{ selectedDate }} 刷题记录</h4>
        <div v-if="loadingDetails" style="color:var(--text-muted);"><i class="fas fa-spinner fa-spin"></i> 加载中...</div>
        <div v-else-if="dailyDetails.length === 0" style="color:var(--text-muted);">当日无详细记录（可能为旧版数据记录或数据为空）</div>
        <div v-else style="display:flex;flex-direction:column;gap:10px;">
          <div v-for="(item, idx) in dailyDetails" :key="idx"
            style="padding:14px 18px;background:var(--bg-card);border-radius:10px;border:1px solid var(--border);box-shadow:var(--shadow);font-size:15px;line-height:1.6;">
            <i :class="['fas', subjectIcons[item.subject] || 'fa-pen']" style="color:var(--primary);margin-right:4px;"></i>
            <span style="font-weight:700;color:var(--primary-light);margin:0 2px;">{{ item.subject || '综合' }}</span>
            <span style="color:var(--text-muted);margin:0 4px;">-</span>
            <span style="font-weight:600;">{{ item.chapter || '综合练习' }}</span>
            <span style="color:var(--text-muted);margin:0 2px;">：</span>
            <span style="color:var(--accent);font-weight:800;">{{ item.count }}</span>
            <span style="color:var(--text-muted);"> 道题</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.heatmap-cell.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.heatmap-cell.clickable:hover {
  transform: scale(1.2);
  box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  z-index: 10;
}
.heatmap-cell.selected-cell {
  border: 2px solid var(--accent);
  transform: scale(1.1);
  box-shadow: 0 0 8px var(--accent);
}
</style>
