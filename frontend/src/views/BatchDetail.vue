<template>
  <div class="batch-detail-page">
    <el-card class="detail-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">批次执行详情</div>
            <div class="subtitle" v-if="batchDetail">{{ batchDetail.batch_name }}</div>
          </div>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <div v-loading="loading">
        <div v-if="batchDetail">
          <!-- 批次基本信息 -->
          <div class="info-section">
            <h3>批次信息</h3>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="批次名称">{{ batchDetail.batch_name }}</el-descriptions-item>
              <el-descriptions-item label="数据集">{{ batchDetail.dataset_name }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(batchDetail.status)">
                  {{ getStatusText(batchDetail.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="规则数量">{{ batchDetail.rule_ids.length }} 条</el-descriptions-item>
              <el-descriptions-item label="总数据量">{{ batchDetail.total_count }} 条</el-descriptions-item>
              <el-descriptions-item label="已处理">{{ batchDetail.processed_count }} 条</el-descriptions-item>
              <el-descriptions-item label="通过">{{ batchDetail.passed_count }} 条</el-descriptions-item>
              <el-descriptions-item label="失败">{{ batchDetail.failed_count }} 条</el-descriptions-item>
              <el-descriptions-item label="规则列表">
                <el-tag v-for="(ruleName, index) in batchDetail.rule_names" :key="index" style="margin-right: 8px; margin-bottom: 4px;">
                  {{ ruleName }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <el-divider />

          <!-- 搜索和筛选 -->
          <div class="toolbar">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索文件名或数据ID"
              clearable
              style="width: 300px"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterStatus"
              placeholder="筛选结果"
              clearable
              style="width: 150px; margin-left: 12px;"
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="通过" value="passed" />
              <el-option label="不通过" value="failed" />
            </el-select>
            <div style="margin-left: auto; font-size: 14px; color: #909399;">
              共 {{ filteredDataResults.length }} 条记录
            </div>
          </div>

          <!-- 数据项执行结果 -->
          <div class="data-section">
            <h3>数据项执行结果</h3>
            <el-table
              :data="paginatedDataResults"
              border
              stripe
              style="margin-top: 16px;"
              :default-expand-all="false"
            >
              <el-table-column type="expand">
                <template #default="{ row }">
                  <div class="expand-content">
                    <div class="rule-results-title">规则执行详情：</div>
                    <div v-for="(ruleResult, index) in row.rule_results" :key="index" class="rule-result-item">
                      <el-card shadow="never" class="rule-result-card">
                        <div class="rule-result-header">
                          <el-tag
                            :type="ruleResult.passed ? 'success' : ruleResult.flag === -1 ? 'danger' : 'warning'"
                            size="small"
                          >
                            {{ ruleResult.rule_name }}
                          </el-tag>
                          <span class="rule-status">
                            {{ ruleResult.passed ? '通过' : ruleResult.flag === -1 ? '错误' : '不通过' }}
                            <span v-if="ruleResult.deduct > 0" style="color: #f56c6c; margin-left: 8px;">
                              (扣{{ ruleResult.deduct }}分)
                            </span>
                          </span>
                          <el-button
                            link
                            type="primary"
                            size="small"
                            style="margin-left: auto;"
                            @click="viewRuleAnswer(ruleResult)"
                          >
                            查看证据
                          </el-button>
                        </div>
                        <div v-if="ruleResult.explanation" class="rule-explanation">
                          <strong>说明：</strong>{{ ruleResult.explanation }}
                        </div>
                        <div v-if="ruleResult.error" class="rule-error">
                          <strong style="color: #f56c6c;">错误：</strong>{{ ruleResult.error }}
                        </div>
                      </el-card>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column type="index" label="#" width="60" align="center" />
              <el-table-column prop="data_id" label="数据ID" width="100" align="center" />
              <el-table-column prop="file_name" label="文件名" min-width="200" show-overflow-tooltip />
              <el-table-column prop="file_size" label="文件大小" width="120" align="center">
                <template #default="{ row }">
                  {{ formatSize(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column label="通过率" width="120" align="center">
                <template #default="{ row }">
                  <span :style="{ color: getPassRateColor(getPassRate(row)), fontWeight: '600', fontSize: '14px' }">
                    {{ (getPassRate(row) / 100).toFixed(2) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="total_deduct" label="总扣分" width="100" align="center">
                <template #default="{ row }">
                  <span :style="{ color: row.total_deduct > 0 ? '#f56c6c' : '#67c23a' }">
                    {{ row.total_deduct }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="规则结果" min-width="300">
                <template #default="{ row }">
                  <div class="rule-results-summary">
                    <el-tag
                      v-for="(ruleResult, index) in row.rule_results"
                      :key="index"
                      :type="ruleResult.passed ? 'success' : ruleResult.flag === -1 ? 'danger' : 'warning'"
                      size="small"
                      style="margin-right: 8px; margin-bottom: 4px;"
                    >
                      {{ ruleResult.rule_name }}
                      <span v-if="!ruleResult.passed && ruleResult.deduct > 0" style="margin-left: 4px;">
                        (-{{ ruleResult.deduct }})
                      </span>
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="filteredDataResults.length"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无详情数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getBatchDetail, type BatchExecutionDetail } from '@/api/batch'
import { useTabsStore } from '@/stores/tabs'

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

const batchDetail = ref<BatchExecutionDetail | null>(null)
const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 计算通过率
const getPassRate = (row: any): number => {
  if (!row.rule_results || row.rule_results.length === 0) return 0
  const passedCount = row.rule_results.filter((r: any) => r.passed === true).length
  return Math.round((passedCount / row.rule_results.length) * 100)
}

// 获取通过数量
const getPassedCount = (row: any): number => {
  if (!row.rule_results) return 0
  return row.rule_results.filter((r: any) => r.passed === true).length
}

// 获取通过率颜色
const getPassRateColor = (rate: number): string => {
  if (rate >= 80) return '#67c23a' // 绿色
  if (rate >= 60) return '#e6a23c' // 橙色
  if (rate >= 40) return '#f56c6c' // 红色
  return '#f56c6c' // 红色
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

// 过滤后的数据结果
const filteredDataResults = computed(() => {
  if (!batchDetail.value) return []
  
  let results = batchDetail.value.data_results
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    results = results.filter(item =>
      item.file_name.toLowerCase().includes(keyword) ||
      item.data_id.toString().includes(keyword)
    )
  }
  
  // 状态过滤（基于通过率）
  if (filterStatus.value) {
    if (filterStatus.value === 'passed') {
      results = results.filter(item => getPassRate(item) === 100)
    } else if (filterStatus.value === 'failed') {
      results = results.filter(item => getPassRate(item) < 100)
    }
  }
  
  return results
})

// 分页后的数据结果
const paginatedDataResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDataResults.value.slice(start, end)
})

// 加载批次详情
const loadBatchDetail = async () => {
  const batchId = route.params.id
  if (!batchId || isNaN(Number(batchId))) {
    ElMessage.error('无效的批次ID')
    router.push('/batches')
    return
  }

  loading.value = true
  try {
    const detail = await getBatchDetail(Number(batchId))
    batchDetail.value = detail
    
    // 更新标签页标题
    const tab = tabsStore.tabs.find(t => t.path === route.path)
    if (tab) {
      tab.title = `批次详情: ${detail.batch_name}`
    }
  } catch (error: any) {
    ElMessage.error('加载批次详情失败: ' + (error.message || '未知错误'))
    router.push('/batches')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 分页
const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {
  // 分页变化时自动滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 查看规则证据
const viewRuleAnswer = (ruleResult: any) => {
  try {
    ElMessageBox.alert(
      `<div style="max-height: 70vh; overflow: auto;"><pre style="text-align: left; margin: 0; padding: 16px; background: #f5f7fa; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; word-break: break-all;">${JSON.stringify(ruleResult.answer || {}, null, 2)}</pre></div>`,
      `规则证据 - ${ruleResult.rule_name}`,
      {
        dangerouslyUseHTMLString: true,
        customClass: 'json-view-dialog',
        confirmButtonText: '关闭',
        width: '90%',
        maxWidth: '1200px'
      }
    ).catch(() => {})
  } catch (error) {
    // 用户取消或关闭
  }
}

// 返回
const goBack = () => {
  router.push('/batches')
}

onMounted(() => {
  loadBatchDetail()
})
</script>

<style scoped>
.batch-detail-page {
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

.data-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.expand-content {
  padding: 16px;
  background: #fafafa;
}

.rule-results-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.rule-result-item {
  margin-bottom: 12px;
}

.rule-result-item:last-child {
  margin-bottom: 0;
}

.rule-result-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
}

.rule-result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.rule-status {
  font-size: 14px;
  color: #606266;
}

.rule-explanation {
  margin-top: 8px;
  padding: 8px;
  background: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}

.rule-error {
  margin-top: 8px;
  padding: 8px;
  background: #fef0f0;
  border-left: 3px solid #f56c6c;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #f56c6c;
}

.rule-results-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
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

