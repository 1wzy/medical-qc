<!-- src/views/BatchManage.vue -->
<template>
  <div class="batch-manage" style="padding: 20px; background-color: #f5f7fa; min-height: 100%;">
    <el-card shadow="never" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>批次管理</span>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :model="searchForm" inline>
        <el-form-item label="批次名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入批次名称"
            clearable
            @keyup.enter="handleSearch"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card shadow="never">
      <el-table
        :data="tableData"
        border
        style="width: 100%"
        v-loading="loading"
        row-key="id"
      >
        <el-table-column prop="id" label="批次ID" width="100" align="center" />
        <el-table-column prop="name" label="批次名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="uploadTime" label="上传时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.uploadTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" link type="danger" @click="deleteBatch(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top: 16px; text-align: right;">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 模拟数据接口
interface BatchItem {
  id: number
  name: string
  uploadTime: string // ISO 8601 格式
  status: 'pending' | 'processing' | 'completed' | 'failed'
}

// 搜索表单
const searchForm = ref({
  name: ''
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 加载状态
const loading = ref(false)

// 原始数据（模拟）
const allBatches: BatchItem[] = [
  { id: 16, name: '医院1 批次3', uploadTime: '2025-08-30T14:00:49', status: 'completed' },
  { id: 18, name: '深度质控检测批次', uploadTime: '2025-09-02T10:46:22', status: 'completed' },
  { id: 20, name: '深度质控检测批次-测试', uploadTime: '2025-09-03T13:05:38', status: 'failed' },
  { id: 21, name: '急诊科文书批次', uploadTime: '2025-09-05T09:12:00', status: 'processing' },
  { id: 22, name: '门诊部9月第一周', uploadTime: '2025-09-01T08:30:00', status: 'pending' },
  { id: 23, name: '住院病历抽检', uploadTime: '2025-09-04T16:20:11', status: 'completed' },
  { id: 24, name: 'ICU专项检查', uploadTime: '2025-09-06T11:00:00', status: 'pending' }
]

// 过滤后的表格数据
const tableData = computed(() => {
  let filtered = allBatches

  // 按名称搜索（模糊）
  if (searchForm.value.name) {
    const keyword = searchForm.value.name.trim().toLowerCase()
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(keyword)
    )
  }

  // 更新总数
  pagination.value.total = filtered.length

  // 分页切片
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filtered.slice(start, start + pagination.value.pageSize)
})

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 状态文本
const getStatusText = (status: BatchItem['status']): string => {
  const map: Record<BatchItem['status'], string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status]
}

// 状态标签类型
const getStatusType = (status: BatchItem['status']): '' | 'success' | 'warning' | 'danger' => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return ''
  }
}

// 搜索
const handleSearch = () => {
  pagination.value.currentPage = 1 // 重置到第一页
}

// 重置
const handleReset = () => {
  searchForm.value.name = ''
  pagination.value.currentPage = 1
}

// 分页事件
const handleSizeChange = (val: number) => {
  pagination.value.pageSize = val
}
const handleCurrentChange = () => {
  // 数据已由 computed 自动更新，无需额外操作
}

// 操作方法
const viewDetail = (row: BatchItem) => {
  ElMessage.info(`查看批次【${row.name}】详情（ID: ${row.id}）`)
  // TODO: 跳转到详情页或弹窗
}

const deleteBatch = (id: number) => {
  ElMessageBox.confirm('确定删除该批次？此操作不可恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    // TODO: 调用 API 删除
  }).catch(() => {
    // 取消
  })
}

// 初始化
onMounted(() => {
  pagination.value.total = allBatches.length
})
</script>

<style scoped>
.card-header {
  font-size: 16px;
  font-weight: bold;
}
</style>