<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getRanking } from '../api/ranking'

const period = ref('all')
const dimension = ref('count')
const list = ref<any[]>([])

const loadRanking = async () => {
  const res = await getRanking({ period: period.value, dimension: dimension.value })
  if (res.data.code === 200) list.value = res.data.data
}

const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return 'rank-default'
}

onMounted(loadRanking)
</script>

<template>
  <div class="fade-in">
    <div class="filter-tabs">
      <button class="filter-tab" :class="{ active: period === 'all' }" @click="period = 'all'; loadRanking()">总榜</button>
      <button class="filter-tab" :class="{ active: period === 'month' }" @click="period = 'month'; loadRanking()">月榜</button>
      <button class="filter-tab" :class="{ active: period === 'week' }" @click="period = 'week'; loadRanking()">周榜</button>
      <span style="border-left:1px solid var(--border);margin:0 8px;"></span>
      <button class="filter-tab" :class="{ active: dimension === 'count' }" @click="dimension = 'count'; loadRanking()">
        <i class="fas fa-pencil-alt"></i> 做题数量
      </button>
      <button class="filter-tab" :class="{ active: dimension === 'streak' }" @click="dimension = 'streak'; loadRanking()">
        <i class="fas fa-fire"></i> 连续打卡
      </button>
    </div>

    <div class="card" style="padding:0;overflow:hidden;">
      <div v-for="item in list" :key="item.user_id" class="rank-item">
        <div class="rank-number" :class="getRankClass(item.rank)">{{ item.rank }}</div>
        <div class="avatar" style="width:36px;height:36px;font-size:14px;">
          <img v-if="item.avatar" :src="item.avatar" />
          <span v-else>{{ (item.username || '').charAt(0).toUpperCase() }}</span>
        </div>
        <div style="flex:1;">
          <div style="font-weight:600;">{{ item.username }}</div>
          <div style="font-size:12px;color:var(--text-muted);">{{ item.grade }}</div>
        </div>
        <div style="font-weight:800;font-size:18px;color:var(--primary-light);">
          {{ dimension === 'count' ? item.total_count : item.streak_days }}
          <span style="font-size:12px;color:var(--text-muted);font-weight:400;">
            {{ dimension === 'count' ? '题' : '天' }}
          </span>
        </div>
      </div>

      <div v-if="list.length === 0" class="empty-state">
        <div class="empty-icon"><i class="fas fa-trophy"></i></div>
        <div class="empty-text">暂无排名数据，快去做题吧！</div>
      </div>
    </div>
  </div>
</template>
