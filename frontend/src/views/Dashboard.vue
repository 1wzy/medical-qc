<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-glow"></div>
      <div class="welcome-body">
        <div class="welcome-left">
          <div class="welcome-avatar">
            <el-icon :size="40"><User /></el-icon>
          </div>
          <div class="welcome-text">
            <h1 class="welcome-title">
              欢迎回来，<span class="username">{{ username }}</span> 👋
            </h1>
            <p class="welcome-desc">今天是 {{ currentDate }}，祝您工作愉快！</p>
            <div class="welcome-tags">
              <div class="tag">
                <el-icon><DataAnalysis /></el-icon>
                <span>医疗质控系统</span>
              </div>
              <div class="tag">
                <el-icon><Clock /></el-icon>
                <span>高效模式已开启</span>
              </div>
            </div>
          </div>
        </div>
        <div class="welcome-right">
          <div class="highlight-card">
            <div class="highlight-title">今日关键</div>
            <div class="highlight-values">
              <div class="highlight-value">
                <span class="label">待处理批次</span>
                <span class="value">{{ pendingBatches }}</span>
              </div>
              <div class="highlight-value">
                <span class="label">已完成批次</span>
                <span class="value">{{ completedBatches }}</span>
              </div>
            </div>
            <div class="highlight-footer">保持专注，快速处理即可完成质控任务</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover" v-for="stat in stats" :key="stat.title">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-title">{{ stat.title }}</div>
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-trend" :class="stat.trend.type">
              <el-icon>
                <ArrowUp v-if="stat.trend.type === 'up'" />
                <ArrowDown v-else />
              </el-icon>
              <span>{{ stat.trend.value }}</span>
            </div>
          </div>
          <div class="stat-icon" :style="{ background: stat.color }">
            <el-icon :size="32">
              <component :is="stat.icon" />
            </el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快捷操作 & 最近批次 -->
    <div class="content-grid">
      <el-card class="quick-actions-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Lightning /></el-icon>
            <span>快捷操作</span>
          </div>
        </template>
        <div class="quick-actions">
          <div
            class="action-item"
            v-for="action in quickActions"
            :key="action.title"
            @click="handleAction(action)"
          >
            <div class="action-icon" :style="{ background: action.color }">
              <el-icon :size="20">
                <component :is="action.icon" />
              </el-icon>
            </div>
            <div class="action-info">
              <div class="action-title">{{ action.title }}</div>
              <div class="action-desc">{{ action.desc }}</div>
            </div>
            <el-icon class="action-arrow">
              <ArrowRight />
            </el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="recent-batches-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>最近批次</span>
          </div>
        </template>
        <div class="recent-batches-list">
          <div class="batch-item" v-for="batch in recentBatches" :key="batch.id">
            <div class="batch-icon" :class="getStatusClass(batch.status)">
              <el-icon>
                <component :is="getStatusIcon(batch.status)" />
              </el-icon>
            </div>
            <div class="batch-info">
              <div class="batch-title">{{ batch.name }}</div>
              <div class="batch-time">{{ formatTime(batch.created_at) }}</div>
            </div>
            <el-tag :type="getStatusTagType(batch.status)" size="small">
              {{ getStatusText(batch.status) }}
            </el-tag>
          </div>
          <div v-if="recentBatches.length === 0" class="empty-state">
            <el-empty description="暂无批次数据" :image-size="80" />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近动态 -->
    <el-card class="recent-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>最近动态</span>
        </div>
      </template>
      <div class="activity-list wide">
        <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
          <div class="activity-avatar" :style="{ background: activity.color }">
            <el-icon>
              <component :is="activity.icon" />
            </el-icon>
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-time">{{ activity.time }}</div>
          </div>
          <el-tag size="small" type="info">{{ activity.type }}</el-tag>
        </div>
        <div v-if="recentActivities.length === 0" class="empty-state">
          <el-empty description="暂无动态" :image-size="80" />
        </div>
      </div>
    </el-card>

    <!-- 批次状态统计 -->
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><PieChart /></el-icon>
          <span>批次状态统计（7天）</span>
        </div>
      </template>
      <div class="status-chart">
        <div class="status-row" v-for="item in statusData" :key="item.label">
          <div class="status-label">{{ item.label }}</div>
          <div class="status-bar-wrap">
            <div class="status-bar" :style="{ width: item.percent + '%', background: item.color }"></div>
          </div>
          <div class="status-value">{{ item.value }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  User,
  DataAnalysis,
  Clock,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  Lightning,
  Document,
  PieChart,
  Setting,
  Folder,
  Files,
  List,
  Check,
  Loading,
  Warning,
  CircleClose
} from '@element-plus/icons-vue'
import { getRules } from '@/api/rule'
import { getRuleSets } from '@/api/ruleSet'
import { getBatchList } from '@/api/batch'
import { getBasicDataList, getDatasetList } from '@/api/data'
import type { Batch } from '@/api/batch'

defineOptions({ name: 'Dashboard' })

const router = useRouter()

// 获取用户名
const username = computed(() => {
  return localStorage.getItem('username') || '管理员'
})

// 当前日期
const currentDate = computed(() => {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const weekday = weekdays[date.getDay()]
  return `${year}年${month}月${day}日 ${weekday}`
})

// 统计数据
const stats = ref([
  {
    title: '规则总数',
    value: '--',
    trend: { type: 'up', value: '已启用' },
    icon: Setting,
    color: '#409EFF',
  },
  {
    title: '规则集数量',
    value: '--',
    trend: { type: 'up', value: '已配置' },
    icon: List,
    color: '#10B981',
  },
  {
    title: '批次总数',
    value: '--',
    trend: { type: 'up', value: '进行中' },
    icon: Files,
    color: '#F59E0B',
  },
  {
    title: '数据总数',
    value: '--',
    trend: { type: 'up', value: '已上传' },
    icon: Folder,
    color: '#EF4444',
  },
])

// 快捷操作
const quickActions = ref([
  {
    title: '规则管理',
    desc: '创建和管理质控规则',
    icon: Setting,
    color: '#409EFF',
    path: '/rule/manage',
  },
  {
    title: '规则集管理',
    desc: '配置规则集合',
    icon: List,
    color: '#10B981',
    path: '/rule/set',
  },
  {
    title: '数据管理',
    desc: '上传和管理基础数据',
    icon: Folder,
    color: '#F59E0B',
    path: '/data/basic',
  },
  {
    title: '批次管理',
    desc: '执行质控批次任务',
    icon: Files,
    color: '#EF4444',
    path: '/batches',
  },
])

// 最近批次
const recentBatches = ref<Batch[]>([])
const pendingBatches = computed(() => {
  return recentBatches.value.filter(b => b.status === 'pending' || b.status === 'processing').length
})
const completedBatches = computed(() => {
  return recentBatches.value.filter(b => b.status === 'completed').length
})

// 最近动态
const recentActivities = ref<
  { id: string; title: string; time: string; icon: any; color: string; type: string }[]
>([])

// 批次状态统计
const statusData = ref<{ label: string; value: number; percent: number; color: string }[]>([])

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return '刚刚'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 获取状态样式
const getStatusClass = (status: string) => {
  const map: Record<string, string> = {
    pending: 'status-pending',
    processing: 'status-processing',
    completed: 'status-completed',
    failed: 'status-failed',
  }
  return map[status] || 'status-pending'
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  const map: Record<string, any> = {
    pending: Clock,
    processing: Loading,
    completed: Check,
    failed: CircleClose,
  }
  return map[status] || Clock
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}

// 处理快捷操作
const handleAction = (action: { path?: string }) => {
  if (action.path) {
    router.push(action.path)
  }
}

// 格式化数字
const formatNumber = (num: number) => {
  return num > 9999 ? `${(num / 10000).toFixed(1)}w` : `${num}`
}

// 加载数据
const loadDashboardData = async () => {
  try {
    // 并行加载所有数据
    const [rulesRes, ruleSetsRes, batchesRes, basicDataRes, datasetRes] = await Promise.all([
      getRules().catch(() => ({ data: [] })),
      getRuleSets().catch(() => ({ data: [] })),
      getBatchList({ skip: 0, limit: 100 }).catch(() => ({ items: [], total: 0 })),
      getBasicDataList({ skip: 0, limit: 1 }).catch(() => ({ items: [], total: 0 })),
      getDatasetList({ skip: 0, limit: 1 }).catch(() => ({ items: [], total: 0 })),
    ])

    // 规则数据
    const rules = Array.isArray(rulesRes) ? rulesRes : rulesRes.data || []
    const ruleCount = rules.length
    const activeRules = rules.filter((r: any) => r.status === 'published' || r.status === 'active').length

    // 规则集数据
    const ruleSets = Array.isArray(ruleSetsRes) ? ruleSetsRes : ruleSetsRes.data || []
    const ruleSetCount = ruleSets.length

    // 批次数据
    const batches = batchesRes.items || []
    const batchTotal = batchesRes.total || batches.length
    recentBatches.value = batches
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5)

    // 数据统计
    const basicDataTotal = basicDataRes.total || 0
    const datasetTotal = datasetRes.total || 0
    const dataTotal = basicDataTotal + datasetTotal

    // 更新统计卡片
    stats.value = [
      {
        title: '规则总数',
        value: formatNumber(ruleCount),
        trend: { type: 'up', value: `已启用 ${activeRules}` },
        icon: Setting,
        color: '#409EFF',
      },
      {
        title: '规则集数量',
        value: formatNumber(ruleSetCount),
        trend: { type: 'up', value: '已配置' },
        icon: List,
        color: '#10B981',
      },
      {
        title: '批次总数',
        value: formatNumber(batchTotal),
        trend: { type: 'up', value: `进行中 ${batches.filter((b: Batch) => b.status === 'processing').length}` },
        icon: Files,
        color: '#F59E0B',
      },
      {
        title: '数据总数',
        value: formatNumber(dataTotal),
        trend: { type: 'up', value: `基础数据 ${basicDataTotal}` },
        icon: Folder,
        color: '#EF4444',
      },
    ]

    // 最近动态（规则、规则集、批次）
    const activities: any[] = []

    // 最近规则
    const recentRules = [...rules]
      .sort((a: any, b: any) => new Date(b.created_at || b.updated_at || 0).getTime() - new Date(a.created_at || a.updated_at || 0).getTime())
      .slice(0, 2)
      .map((r: any) => ({
        id: `rule-${r.id}`,
        title: `新规则：${r.name}`,
        time: formatTime(r.created_at || r.updated_at),
        icon: Setting,
        color: '#409EFF',
        type: '规则',
      }))

    // 最近规则集
    const recentRuleSets = [...ruleSets]
      .sort((a: any, b: any) => new Date(b.created_at || b.updated_at || 0).getTime() - new Date(a.created_at || a.updated_at || 0).getTime())
      .slice(0, 2)
      .map((rs: any) => ({
        id: `ruleset-${rs.id}`,
        title: `新规则集：${rs.name}`,
        time: formatTime(rs.created_at || rs.updated_at),
        icon: List,
        color: '#10B981',
        type: '规则集',
      }))

    // 最近批次
    const recentBatchActivities = recentBatches.value.slice(0, 3).map((b) => ({
      id: `batch-${b.id}`,
      title: `批次：${b.name}`,
      time: formatTime(b.created_at),
      icon: Files,
      color: '#F59E0B',
      type: '批次',
    }))

    recentActivities.value = [...recentRules, ...recentRuleSets, ...recentBatchActivities]

    // 批次状态统计（最近7天）
    const last7Days = Array.from({ length: 7 })
      .map((_, idx) => {
        const day = new Date()
        day.setDate(day.getDate() - (6 - idx))
        return day
      })
      .map((day) => {
        const dayBatches = batches.filter((b: Batch) => {
          const batchDate = new Date(b.created_at)
          return batchDate.toDateString() === day.toDateString()
        })
        return {
          date: day,
          pending: dayBatches.filter((b: Batch) => b.status === 'pending').length,
          processing: dayBatches.filter((b: Batch) => b.status === 'processing').length,
          completed: dayBatches.filter((b: Batch) => b.status === 'completed').length,
          failed: dayBatches.filter((b: Batch) => b.status === 'failed').length,
        }
      })

    const maxValue = Math.max(
      ...last7Days.flatMap((d) => [d.pending, d.processing, d.completed, d.failed]),
      1
    )

    statusData.value = [
      {
        label: '待处理',
        value: last7Days.reduce((sum, d) => sum + d.pending, 0),
        percent: Math.round((last7Days.reduce((sum, d) => sum + d.pending, 0) / maxValue) * 100),
        color: '#909399',
      },
      {
        label: '处理中',
        value: last7Days.reduce((sum, d) => sum + d.processing, 0),
        percent: Math.round((last7Days.reduce((sum, d) => sum + d.processing, 0) / maxValue) * 100),
        color: '#E6A23C',
      },
      {
        label: '已完成',
        value: last7Days.reduce((sum, d) => sum + d.completed, 0),
        percent: Math.round((last7Days.reduce((sum, d) => sum + d.completed, 0) / maxValue) * 100),
        color: '#67C23A',
      },
      {
        label: '失败',
        value: last7Days.reduce((sum, d) => sum + d.failed, 0),
        percent: Math.round((last7Days.reduce((sum, d) => sum + d.failed, 0) / maxValue) * 100),
        color: '#F56C6C',
      },
    ]
  } catch (error) {
    console.error('加载工作台数据失败:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  background: #f4f6f9;
  min-height: 100%;
  padding: 0;
}

/* 欢迎区域 */
.welcome-section {
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
  padding: 24px;
  border-radius: 14px;
  background: linear-gradient(
    135deg,
    rgba(64, 158, 255, 0.16) 0%,
    rgba(64, 158, 255, 0.08) 50%,
    #ffffff 100%
  );
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
}

.welcome-section .welcome-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at 30% 50%,
    rgba(64, 158, 255, 0.08) 0%,
    transparent 45%
  );
  filter: blur(24px);
  opacity: 0.7;
  pointer-events: none;
}

.welcome-section .welcome-body {
  position: relative;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
  align-items: stretch;
  z-index: 1;
}

.welcome-section .welcome-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.welcome-section .welcome-left .welcome-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 10px 26px rgba(64, 158, 255, 0.3);
}

.welcome-section .welcome-left .welcome-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.welcome-section .welcome-left .welcome-title {
  font-size: 30px;
  font-weight: 800;
  color: #303133;
  margin: 0;
  letter-spacing: 0.3px;
}

.welcome-section .welcome-left .welcome-title .username {
  color: #409eff;
}

.welcome-section .welcome-left .welcome-desc {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.welcome-section .welcome-left .welcome-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.welcome-section .welcome-left .welcome-tags .tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.16);
  color: #303133;
  font-size: 12px;
}

.welcome-section .welcome-left .welcome-tags .tag .el-icon {
  color: #409eff;
}

.welcome-section .welcome-right {
  display: flex;
  align-items: stretch;
}

.welcome-section .welcome-right .highlight-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(64, 158, 255, 0.24);
  box-shadow: 0 10px 26px rgba(64, 158, 255, 0.15);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.welcome-section .welcome-right .highlight-card .highlight-title {
  font-size: 14px;
  font-weight: 700;
  color: #303133;
}

.welcome-section .welcome-right .highlight-card .highlight-values {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}

.welcome-section .welcome-right .highlight-card .highlight-values .highlight-value {
  padding: 12px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-section .welcome-right .highlight-card .highlight-values .highlight-value .label {
  color: #606266;
  font-size: 12px;
}

.welcome-section .welcome-right .highlight-card .highlight-values .highlight-value .value {
  font-size: 20px;
  font-weight: 800;
  color: #409eff;
}

.welcome-section .welcome-right .highlight-card .highlight-footer {
  font-size: 12px;
  color: #606266;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stats-grid .stat-card {
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.stats-grid .stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stats-grid .stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stats-grid .stat-card .stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-grid .stat-card .stat-content .stat-info {
  flex: 1;
}

.stats-grid .stat-card .stat-content .stat-info .stat-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.stats-grid .stat-card .stat-content .stat-info .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.stats-grid .stat-card .stat-content .stat-info .stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.stats-grid .stat-card .stat-content .stat-info .stat-trend.up {
  color: #67c23a;
}

.stats-grid .stat-card .stat-content .stat-info .stat-trend.down {
  color: #f56c6c;
}

.stats-grid .stat-card .stat-content .stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

/* 卡片通用样式 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-header .el-icon {
  color: #409eff;
}

/* 快捷操作卡片 */
.quick-actions-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.quick-actions-card :deep(.el-card__body) {
  padding: 16px;
}

.quick-actions-card .quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-actions-card .quick-actions .action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-actions-card .quick-actions .action-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.quick-actions-card .quick-actions .action-item .action-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.quick-actions-card .quick-actions .action-item .action-info {
  flex: 1;
}

.quick-actions-card .quick-actions .action-item .action-info .action-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.quick-actions-card .quick-actions .action-item .action-info .action-desc {
  font-size: 13px;
  color: #606266;
}

.quick-actions-card .quick-actions .action-item .action-arrow {
  color: #909399;
  transition: all 0.3s ease;
}

.quick-actions-card .quick-actions .action-item:hover .action-arrow {
  color: #409eff;
  transform: translateX(4px);
}

.recent-batches-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.recent-batches-card :deep(.el-card__body) {
  padding: 16px;
}

.recent-batches-card .recent-batches-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-batches-card .recent-batches-list .batch-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #ebeef5;
}

.recent-batches-card .recent-batches-list .batch-item .batch-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.recent-batches-card .recent-batches-list .batch-item .batch-icon.status-pending {
  background: #909399;
}

.recent-batches-card .recent-batches-list .batch-item .batch-icon.status-processing {
  background: #e6a23c;
}

.recent-batches-card .recent-batches-list .batch-item .batch-icon.status-completed {
  background: #67c23a;
}

.recent-batches-card .recent-batches-list .batch-item .batch-icon.status-failed {
  background: #f56c6c;
}

.recent-batches-card .recent-batches-list .batch-item .batch-info {
  flex: 1;
}

.recent-batches-card .recent-batches-list .batch-item .batch-info .batch-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.recent-batches-card .recent-batches-list .batch-item .batch-info .batch-time {
  font-size: 12px;
  color: #909399;
}

.recent-batches-card .recent-batches-list .empty-state {
  padding: 20px;
  text-align: center;
}

.recent-card,
.status-card {
  margin-bottom: 24px;
  border-radius: 8px;
  border: 1px solid #ebeef5;

  :deep(.el-card__body) {
    padding: 16px;
  }
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.activity-list.wide .activity-item {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.activity-list .activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-list .activity-item .activity-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.activity-list .activity-item .activity-content {
  flex: 1;
}

.activity-list .activity-item .activity-content .activity-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.activity-list .activity-item .activity-content .activity-time {
  font-size: 12px;
  color: #909399;
}

.activity-list .empty-state {
  padding: 20px;
  text-align: center;
}

.status-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-chart .status-row {
  display: grid;
  grid-template-columns: 70px 1fr 50px;
  align-items: center;
  gap: 10px;
}

.status-chart .status-row .status-label {
  font-size: 12px;
  color: #606266;
}

.status-chart .status-row .status-bar-wrap {
  background: #f5f7fa;
  border-radius: 999px;
  overflow: hidden;
  height: 8px;
  border: 1px solid #ebeef5;
}

.status-chart .status-row .status-bar-wrap .status-bar {
  height: 100%;
  border-radius: 999px;
}

.status-chart .status-row .status-value {
  font-size: 12px;
  color: #303133;
  text-align: right;
}
</style>

