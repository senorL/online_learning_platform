<script setup lang="ts">
import { ref } from 'vue'
import { updateProfile } from '../api/auth'

const safeGetItem = (key: string) => {
  try {
    const val = localStorage.getItem(key)
    return val === 'undefined' || val === 'null' ? '' : (val || '')
  } catch(e) {
    return ''
  }
}

const grade = ref(safeGetItem('grade') || '七年级')
const password = ref('')
const avatarPreview = ref(safeGetItem('avatar'))
const avatarData = ref('')
const username = ref(safeGetItem('username'))

const handleFile = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 1024 * 1024) { alert('图片请控制在1MB以内'); return }
  const reader = new FileReader()
  reader.onload = (ev) => {
    avatarPreview.value = ev.target?.result as string
    avatarData.value = ev.target?.result as string
  }
  reader.readAsDataURL(file)
}

const saveProfile = async () => {
  const data: any = { grade: grade.value }
  if (password.value) data.password = password.value
  if (avatarData.value) data.avatar = avatarData.value

  const res = await updateProfile(data)
  if (res.data.code === 200) {
    alert('资料更新成功！')
    localStorage.setItem('grade', grade.value)
    if (avatarData.value) localStorage.setItem('avatar', avatarData.value)
    password.value = ''
    window.dispatchEvent(new Event('profile-updated'))
  }
}
</script>

<template>
  <div class="fade-in" style="max-width:480px;margin:0 auto;">
    <div class="card">
      <h3 style="font-size:20px;font-weight:700;margin-bottom:24px;">
        <i class="fas fa-id-card" style="color:var(--primary-light);margin-right:8px;"></i>个人信息设置
      </h3>

      <div class="form-group">
        <label>用户名</label>
        <div class="form-readonly">
          {{ username }} (不可修改)
        </div>
      </div>

      <div class="form-group">
        <label>所属年级</label>
        <select v-model="grade" class="form-select">
          <option value="七年级">七年级</option>
          <option value="八年级">八年级</option>
          <option value="九年级">九年级</option>
        </select>
      </div>

      <div class="form-group">
        <label>新密码</label>
        <input v-model="password" type="password" class="form-input" placeholder="不修改请留空" />
      </div>

      <div class="form-group">
        <label>上传头像</label>
        <div style="display:flex;align-items:center;gap:16px;">
          <label class="btn btn-ghost btn-sm" style="cursor:pointer;">
            <i class="fas fa-camera"></i> 选择图片
            <input type="file" accept="image/*" @change="handleFile" style="display:none;" />
          </label>
          <div v-if="avatarPreview" class="avatar" style="width:48px;height:48px;">
            <img :src="avatarPreview" />
          </div>
        </div>
      </div>

      <button @click="saveProfile" class="btn btn-primary btn-full" style="margin-top:8px;">
        <i class="fas fa-save"></i> 保存修改
      </button>
    </div>
  </div>
</template>
