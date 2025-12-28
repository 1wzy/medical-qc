<template>
  <div class="data-page">
    <el-card class="data-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">基础数据管理</div>
            <div class="subtitle">上传和管理JSON格式的基础数据文件</div>
          </div>
          <el-button type="primary" :disabled="fileList.length === 0" @click="handleSubmit">
            提交上传
          </el-button>
        </div>
      </template>

      <!-- 上传区域 -->
      <el-upload
        class="upload-area"
        drag
        multiple
        :auto-upload="false"
        :file-list="fileList"
        :on-change="handleChange"
        :on-remove="handleRemove"
        :limit="50"
        :on-exceed="handleExceed"
        accept=".json"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将JSON文件拖到此处，或 <em>点击上传</em>
        </div>
        <div class="el-upload__tip">
          仅支持 JSON 格式文件，单个文件不超过 50MB
        </div>
      </el-upload>

      <!-- 数据列表 -->
      <el-divider>已上传数据</el-divider>
      
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文件名或ID"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="danger" :disabled="selectedRows.length === 0" @click="handleBatchDelete">
          批量删除
        </el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="filteredDataList"
        size="small"
        class="data-table"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="id" label="数据ID" width="120" show-overflow-tooltip />
        <el-table-column prop="file_name" label="文件名" min-width="260" show-overflow-tooltip />
        <el-table-column prop="file_size" label="大小" width="120" align="center">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" align="center" />
        <el-table-column label="状态" width="120" align="center">
          <template #default>
            <el-tag type="success">已上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { UploadFile, UploadProps } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Search } from '@element-plus/icons-vue'
import {
  getBasicDataList,
  getBasicData,
  uploadBasicData,
  deleteBasicData,
  batchDeleteBasicData,
  type BasicData
} from '@/api/data'

const fileList = ref<UploadFile[]>([])
const dataList = ref<BasicData[]>([])
const searchKeyword = ref('')
const selectedRows = ref<BasicData[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// 加载数据列表
const loadDataList = async () => {
  loading.value = true
  try {
    const response = await getBasicDataList({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchKeyword.value || undefined
    })
    dataList.value = response.items
    total.value = response.total
  } catch (error: any) {
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 初始化加载
onMounted(() => {
  loadDataList()
})

const filteredDataList = computed(() => {
  // 后端已处理搜索，这里直接返回
  return dataList.value
})

const handleChange: UploadProps['onChange'] = (file, files) => {
  // 验证文件类型
  if (file.raw && !file.raw.name.endsWith('.json')) {
    ElMessage.error('只能上传JSON格式的文件')
    const index = files.findIndex((f) => f.uid === file.uid)
    if (index > -1) {
      files.splice(index, 1)
    }
    return
  }
  fileList.value = files
}

const handleRemove: UploadProps['onRemove'] = (file, files) => {
  if (files) {
    fileList.value = files
  }
}

const handleExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('单次最多上传 50 个文件')
}

const formatSize = (size?: number) => {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

const handleSubmit = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的JSON文件')
    return
  }

  try {
    // 逐个上传文件
    for (const file of fileList.value) {
      if (file.raw) {
        await uploadBasicData(file.raw)
      }
    }
    
    ElMessage.success(`成功上传 ${fileList.value.length} 个文件`)
    fileList.value = []
    // 重新加载列表
    await loadDataList()
  } catch (error: any) {
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadDataList()
}

const handleSelectionChange = (selection: DataItem[]) => {
  selectedRows.value = selection
}

const handleView = async (row: BasicData) => {
  try {
    // 获取完整的JSON数据
    const fullData = await getBasicData(row.id)
    // 格式化JSON显示
    const formattedJson = JSON.stringify(fullData.data_content, null, 2)
    try {
      await ElMessageBox.alert(
        `<div style="max-height: 70vh; overflow: auto;"><pre style="text-align: left; margin: 0; padding: 16px; background: #f5f7fa; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; word-break: break-all;">${formattedJson}</pre></div>`,
        `查看数据: ${row.file_name}`,
        {
          dangerouslyUseHTMLString: true,
          customClass: 'json-view-dialog',
          confirmButtonText: '关闭',
          width: '90%',
          maxWidth: '1200px'
        }
      )
    } catch (error: any) {
      // 用户点击右上角 × 或按 ESC 关闭对话框时，会 reject promise
      // 这是正常行为，不需要显示错误
      if (error !== 'cancel' && error !== 'close') {
        console.error('查看数据对话框错误:', error)
      }
    }
  } catch (error: any) {
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  }
}

const handleDelete = async (row: BasicData) => {
  try {
    await ElMessageBox.confirm(`确定要删除数据 "${row.file_name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteBasicData(row.id)
    ElMessage.success('删除成功')
    await loadDataList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条数据吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const idsToDelete = selectedRows.value.map((row) => row.id)
    await batchDeleteBasicData(idsToDelete)
    selectedRows.value = []
    ElMessage.success('批量删除成功')
    await loadDataList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadDataList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadDataList()
}
</script>

<style scoped>
.data-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.data-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.upload-area {
  width: 100%;
  margin-bottom: 20px;
}

.upload-icon {
  font-size: 40px;
  color: #409eff;
  margin-bottom: 8px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.data-table {
  margin-top: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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

