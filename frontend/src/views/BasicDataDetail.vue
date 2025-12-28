<template>
  <div class="basic-data-detail-page">
    <el-card class="detail-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">基础数据详情</div>
            <div class="subtitle" v-if="basicData">{{ basicData.file_name }}</div>
          </div>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-loading="loading">
        <div v-if="basicData">
          <!-- 基本信息 -->
          <div class="info-section">
            <h3>基本信息</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="数据ID">{{ basicData.id }}</el-descriptions-item>
              <el-descriptions-item label="文件名">{{ basicData.file_name }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatSize(basicData.file_size) }}</el-descriptions-item>
              <el-descriptions-item label="数据类型">{{ basicData.data_type || 'JSON' }}</el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">
                {{ basicData.description || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ basicData.created_at }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ basicData.updated_at }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <el-divider />

          <!-- 视图切换标签 -->
          <div class="view-tabs">
            <el-radio-group v-model="viewType" size="default">
              <el-radio-button label="medical">病历视图</el-radio-button>
              <el-radio-button label="json">JSON视图</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 病历视图 -->
          <div v-if="viewType === 'medical'" class="medical-section">
            <MedicalRecordView :data="basicData.data_content" />
          </div>

          <!-- JSON内容展示 -->
          <div v-else class="json-section">
            <div class="json-header">
              <h3>JSON 内容</h3>
              <div class="json-actions">
                <el-button size="small" @click="copyJson">复制JSON</el-button>
                <el-button size="small" @click="downloadJson">下载JSON</el-button>
                <el-button size="small" @click="toggleViewMode">
                  {{ viewMode === 'formatted' ? '原始格式' : '格式化' }}
                </el-button>
              </div>
            </div>
            
            <div class="json-container">
              <div v-if="viewMode === 'formatted'" class="json-viewer">
                <pre ref="jsonPreRef" class="json-content">{{ formattedJson }}</pre>
              </div>
              <div v-else class="json-viewer">
                <pre ref="jsonPreRef" class="json-content">{{ rawJson }}</pre>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getBasicData, type BasicData } from '@/api/data'
import { useTabsStore } from '@/stores/tabs'
import MedicalRecordView from '@/components/MedicalRecordView.vue'

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

const basicData = ref<BasicData | null>(null)
const loading = ref(false)
const viewType = ref<'medical' | 'json'>('medical')
const viewMode = ref<'formatted' | 'raw'>('formatted')
const jsonPreRef = ref<HTMLElement>()

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化后的JSON
const formattedJson = computed(() => {
  if (!basicData.value || !basicData.value.data_content) return ''
  try {
    return JSON.stringify(basicData.value.data_content, null, 2)
  } catch (error) {
    return String(basicData.value.data_content)
  }
})

// 原始JSON
const rawJson = computed(() => {
  if (!basicData.value || !basicData.value.data_content) return ''
  try {
    return JSON.stringify(basicData.value.data_content)
  } catch (error) {
    return String(basicData.value.data_content)
  }
})

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'formatted' ? 'raw' : 'formatted'
}

// 复制JSON
const copyJson = async () => {
  try {
    const jsonText = viewMode.value === 'formatted' ? formattedJson.value : rawJson.value
    await navigator.clipboard.writeText(jsonText)
    ElMessage.success('JSON已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = viewMode.value === 'formatted' ? formattedJson.value : rawJson.value
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('JSON已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

// 下载JSON
const downloadJson = () => {
  if (!basicData.value) return
  
  try {
    const jsonText = viewMode.value === 'formatted' ? formattedJson.value : rawJson.value
    const blob = new Blob([jsonText], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = basicData.value.file_name || `data_${basicData.value.id}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('JSON文件下载成功')
  } catch (error) {
    ElMessage.error('下载失败: ' + (error instanceof Error ? error.message : '未知错误'))
  }
}

// 加载基础数据详情
const loadBasicDataDetail = async () => {
  const dataId = route.params.id
  if (!dataId || isNaN(Number(dataId))) {
    ElMessage.error('无效的数据ID')
    router.push('/data/basic')
    return
  }

  loading.value = true
  try {
    const data = await getBasicData(Number(dataId))
    basicData.value = data
    
    // 更新标签页标题
    const tab = tabsStore.tabs.find(t => t.path === route.path)
    if (tab) {
      tab.title = `数据详情: ${data.file_name}`
    }
  } catch (error: any) {
    ElMessage.error('加载数据详情失败: ' + (error.message || '未知错误'))
    router.push('/data/basic')
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/data/basic')
}

onMounted(() => {
  loadBasicDataDetail()
})
</script>

<style scoped>
.basic-data-detail-page {
  padding: 20px;
}

.detail-card {
  min-height: calc(100vh - 200px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.view-tabs {
  margin: 24px 0;
  display: flex;
  justify-content: center;
}

.medical-section {
  margin-top: 24px;
}

.json-section {
  margin-top: 24px;
}

.json-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.json-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.json-actions {
  display: flex;
  gap: 8px;
}

.json-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  background: #ffffff;
}

.json-viewer {
  position: relative;
  max-height: calc(100vh - 400px);
  overflow: auto;
}

.json-content {
  margin: 0;
  padding: 20px;
  background: #fafafa;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.8;
  color: #303133;
  white-space: pre;
  word-wrap: break-word;
  word-break: break-all;
  overflow-wrap: break-word;
  tab-size: 2;
}

/* JSON语法高亮（简单版本） */
.json-content {
  counter-reset: line-number;
}

/* 滚动条样式 */
.json-viewer::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.json-viewer::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.json-viewer::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.json-viewer::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 选中文本样式 */
.json-content::selection {
  background: #b3d4fc;
}

.json-content::-moz-selection {
  background: #b3d4fc;
}
</style>

