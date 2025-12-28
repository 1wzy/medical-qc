<template>
  <div class="batch-manage">
    <el-card class="batch-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">批次管理</div>
            <div class="subtitle">创建批次并执行规则质控</div>
          </div>
          <el-button type="primary" @click="handleCreateBatch">
            创建批次
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索批次名称"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 批次列表 -->
      <el-table
        v-loading="loading"
        :data="filteredBatchList"
        size="small"
        class="batch-table"
        border
      >
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="id" label="批次ID" width="100" align="center" />
        <el-table-column prop="name" label="批次名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="dataset_id" label="数据集ID" width="120" align="center" />
        <el-table-column label="规则数量" width="120" align="center">
          <template #default="{ row }">
            {{ row.rule_ids?.length || 0 }} 条
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.total_count > 0 ? Math.round((row.processed_count / row.total_count) * 100) : 0"
              :status="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'exception' : undefined"
            />
            <div style="margin-top: 4px; font-size: 12px; color: #909399;">
              {{ row.processed_count }} / {{ row.total_count }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="统计" width="180" align="center">
          <template #default="{ row }">
            <div style="font-size: 12px;">
              <span style="color: #67c23a;">通过: {{ row.passed_count }}</span>
              <span style="margin-left: 8px; color: #f56c6c;">失败: {{ row.failed_count }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" />
        <el-table-column label="操作" width="250" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'failed'"
              link
              type="success"
              size="small"
              @click="handleExecute(row)"
            >
              执行
            </el-button>
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

    <!-- 创建批次对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建批次"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="批次名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入批次名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入批次描述（可选）"
          />
        </el-form-item>
        <el-form-item label="数据集" prop="dataset_id">
          <el-select
            v-model="form.dataset_id"
            placeholder="请选择数据集"
            filterable
            style="width: 100%"
            :loading="datasetLoading"
            @focus="loadDatasets"
          >
            <el-option
              v-for="dataset in datasetList"
              :key="dataset.id"
              :label="`${dataset.name} (${dataset.data_count}条)`"
              :value="dataset.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="规则集" prop="rule_set_id">
          <el-select
            v-model="form.rule_set_id"
            placeholder="请选择规则集"
            filterable
            style="width: 100%"
            :loading="ruleSetLoading"
            @focus="loadRuleSets"
          >
            <el-option
              v-for="ruleSet in ruleSetList"
              :key="ruleSet.id"
              :label="`${ruleSet.name} (${ruleSet.rule_count}条规则)`"
              :value="ruleSet.id"
              :disabled="ruleSet.status !== 'active'"
            >
              <div>
                <span>{{ ruleSet.name }}</span>
                <span style="color: #909399; font-size: 12px; margin-left: 8px;">
                  {{ ruleSet.rule_count }}条规则
                  <span v-if="ruleSet.status !== 'active'">(未启用)</span>
                </span>
              </div>
            </el-option>
          </el-select>
          <div v-if="form.rule_set_id" style="margin-top: 8px; font-size: 12px; color: #909399;">
            {{ getSelectedRuleSetInfo() }}
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveBatch" :loading="submitting">
          创建
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import {
  getBatchList,
  createBatch,
  deleteBatch,
  executeBatch,
  type Batch
} from '@/api/batch'
import { getDatasetList, type Dataset } from '@/api/data'
import { getRules, type Rule } from '@/api/rule'
import { getRuleSets, type RuleSet } from '@/api/ruleSet'

const router = useRouter()
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const batchList = ref<Batch[]>([])
const datasetList = ref<Dataset[]>([])
const ruleSetList = ref<RuleSet[]>([])
const datasetLoading = ref(false)
const ruleSetLoading = ref(false)

const form = reactive({
  name: '',
  description: '',
  dataset_id: undefined as number | undefined,
  rule_set_id: undefined as number | undefined
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入批次名称', trigger: 'blur' }
  ],
  dataset_id: [
    { required: true, message: '请选择数据集', trigger: 'change' }
  ],
  rule_set_id: [
    { required: true, message: '请选择规则集', trigger: 'change' }
  ]
}

// 过滤后的批次列表
const filteredBatchList = computed(() => {
  let filtered = batchList.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(keyword) ||
      item.id.toString().includes(keyword)
    )
  }

  total.value = filtered.length

  const start = (currentPage.value - 1) * pageSize.value
  return filtered.slice(start, start + pageSize.value)
})

// 加载批次列表
const loadBatchList = async () => {
  loading.value = true
  try {
    const response = await getBatchList({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchKeyword.value || undefined
    })
    batchList.value = response.items
    total.value = response.total
  } catch (error: any) {
    ElMessage.error('加载批次列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 加载数据集列表
const loadDatasets = async () => {
  if (datasetList.value.length > 0) return
  
  datasetLoading.value = true
  try {
    const response = await getDatasetList({ limit: 1000 })
    datasetList.value = response.items
  } catch (error: any) {
    ElMessage.error('加载数据集列表失败: ' + (error.message || '未知错误'))
  } finally {
    datasetLoading.value = false
  }
}

// 加载规则集列表
const loadRuleSets = async () => {
  if (ruleSetList.value.length > 0) return
  
  ruleSetLoading.value = true
  try {
    const ruleSets = await getRuleSets()
    ruleSetList.value = ruleSets.filter(rs => rs.status === 'active')
  } catch (error: any) {
    ElMessage.error('加载规则集列表失败: ' + (error.message || '未知错误'))
  } finally {
    ruleSetLoading.value = false
  }
}

// 获取选中的规则集信息
const getSelectedRuleSetInfo = (): string => {
  const selected = ruleSetList.value.find(rs => rs.id === form.rule_set_id)
  if (selected) {
    return `已选择规则集: ${selected.name}，包含 ${selected.rule_count} 条规则`
  }
  return ''
}

// 状态文本
const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 状态标签类型
const getStatusType = (status: string): '' | 'success' | 'warning' | 'danger' => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return ''
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadBatchList()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadBatchList()
}

const handleCurrentChange = () => {
  loadBatchList()
}

// 创建批次
const handleCreateBatch = () => {
  form.name = ''
  form.description = ''
  form.dataset_id = undefined
  form.rule_set_id = undefined
  dialogVisible.value = true
  loadDatasets()
  loadRuleSets()
}

// 保存批次
const handleSaveBatch = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await createBatch({
          name: form.name,
          description: form.description || undefined,
          dataset_id: form.dataset_id!,
          rule_set_id: form.rule_set_id
        })
        ElMessage.success('创建批次成功')
        dialogVisible.value = false
        loadBatchList()
      } catch (error: any) {
        ElMessage.error('创建批次失败: ' + (error.message || '未知错误'))
      } finally {
        submitting.value = false
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 查看批次详情
const handleView = (row: Batch) => {
  router.push(`/batches/${row.id}`)
}

// 执行批次
const handleExecute = async (row: Batch) => {
  try {
    await ElMessageBox.confirm(
      `确定要执行批次 "${row.name}" 吗？`,
      '确认执行',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    try {
      await executeBatch(row.id)
      ElMessage.success('批次执行已开始')
      loadBatchList()
      
      // 如果批次正在处理，定期刷新状态
      if (row.status === 'processing') {
        const interval = setInterval(async () => {
          await loadBatchList()
          const updatedBatch = batchList.value.find(b => b.id === row.id)
          if (updatedBatch && updatedBatch.status !== 'processing') {
            clearInterval(interval)
            ElMessage.success('批次执行完成')
          }
        }, 2000)
        
        // 30秒后停止刷新
        setTimeout(() => {
          clearInterval(interval)
        }, 30000)
      }
    } catch (error: any) {
      ElMessage.error('执行批次失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消
  }
}

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}


// 删除批次
const handleDelete = async (row: Batch) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除批次 "${row.name}" 吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      await deleteBatch(row.id)
      ElMessage.success('删除成功')
      loadBatchList()
    } catch (error: any) {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadBatchList()
})
</script>

<style scoped>
.batch-manage {
  padding: 20px;
}

.batch-card {
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

.toolbar {
  margin-bottom: 16px;
}

.batch-table {
  margin-top: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
