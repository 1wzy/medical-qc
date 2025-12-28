<template>
  <div class="dataset-detail-page">
    <el-card class="detail-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">数据集详情</div>
            <div class="subtitle" v-if="dataset">{{ dataset.name }}</div>
          </div>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-loading="loading" v-if="dataset">
        <!-- 数据集基本信息 -->
        <div class="info-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="数据集名称">{{ dataset.name }}</el-descriptions-item>
            <el-descriptions-item label="数据来源">
              {{ dataset.data_source === 'upload' ? '上传文件' : '从基础数据选择' }}
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ dataset.description || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="数据条数">{{ dataset.data_count }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ dataset.created_at }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ dataset.updated_at }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-divider />

        <!-- 包含的数据 -->
        <div class="data-section">
          <h3>包含的数据</h3>
          <div v-if="dataset.basic_data_list && dataset.basic_data_list.length > 0">
            <el-table
              :data="dataset.basic_data_list"
              size="small"
              border
              style="margin-top: 16px;"
            >
              <el-table-column type="index" label="#" width="60" align="center" />
              <el-table-column prop="id" label="数据ID" width="120" align="center" />
              <el-table-column prop="file_name" label="文件名" min-width="260" show-overflow-tooltip />
              <el-table-column prop="file_size" label="大小" width="120" align="center">
                <template #default="{ row }">
                  {{ formatSize(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="上传时间" width="180" align="center" />
              <el-table-column label="操作" width="120" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="viewBasicDataJson(row.id, row.file_name)">
                    查看JSON
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-else description="该数据集暂无关联的基础数据" />
        </div>
      </div>

      <el-empty v-else-if="!loading" description="数据集不存在或已删除" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasetDetail, getBasicData, type DatasetDetail } from '@/api/data'
import { useTabsStore } from '@/stores/tabs'

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

const dataset = ref<DatasetDetail | null>(null)
const loading = ref(false)

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 加载数据集详情
const loadDatasetDetail = async () => {
  const datasetId = route.params.id
  if (!datasetId || isNaN(Number(datasetId))) {
    ElMessage.error('无效的数据集ID')
    router.push('/data/dataset')
    return
  }

  loading.value = true
  try {
    const data = await getDatasetDetail(Number(datasetId))
    dataset.value = data
    // 更新标签页标题为数据集名称
    const tab = tabsStore.tabs.find(t => t.path === route.path)
    if (tab) {
      tab.title = `数据集: ${data.name}`
    }
  } catch (error: any) {
    ElMessage.error('加载数据集详情失败: ' + (error.message || '未知错误'))
    router.push('/data/dataset')
  } finally {
    loading.value = false
  }
}

// 查看基础数据JSON
const viewBasicDataJson = async (id: number, fileName: string) => {
  try {
    const basicData = await getBasicData(id)
    const jsonContent = typeof basicData.data_content === 'string' 
      ? JSON.parse(basicData.data_content) 
      : basicData.data_content
    
    const formattedJson = JSON.stringify(jsonContent, null, 2)
    
    await ElMessageBox.alert(
      `<div style="max-height: 70vh; overflow: auto;"><pre style="text-align: left; margin: 0; padding: 16px; background: #f5f7fa; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; word-break: break-all;">${formattedJson}</pre></div>`,
      `查看JSON - ${fileName}`,
      {
        dangerouslyUseHTMLString: true,
        customClass: 'json-view-dialog',
        confirmButtonText: '关闭',
        width: '90%',
        maxWidth: '1200px'
      }
    )
  } catch (error: any) {
    // 用户点击关闭或ESC时，ElMessageBox会reject promise，这是正常行为
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('加载JSON数据失败: ' + (error.message || '未知错误'))
    }
  }
}

// 返回
const goBack = () => {
  router.push('/data/dataset')
}

onMounted(() => {
  loadDatasetDetail()
})
</script>

<style scoped>
.dataset-detail-page {
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

.info-section,
.data-section {
  margin-bottom: 24px;
}

.info-section h3,
.data-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

:deep(.json-view-dialog) {
  .el-message-box {
    max-width: 1200px;
  }
  
  .el-message-box__content {
    max-height: 70vh;
    overflow: hidden;
    padding: 0;
  }
  
  .el-message-box__message {
    padding: 0;
  }
  
  pre {
    margin: 0;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
    word-break: break-all;
    max-height: 70vh;
    overflow: auto;
  }
}
</style>

