<template>
  <el-dropdown trigger="click" placement="bottom-end" ref="notificationDropdownRef">
    <el-badge
      :value="unreadCount"
      :hidden="unreadCount === 0"
      :max="99"
      :offset="[-5, 5]"
    >
      <div class="action-btn">
        <el-icon><Bell /></el-icon>
      </div>
    </el-badge>

    <template #dropdown>
      <div class="notification-dropdown">
        <div class="notification-header">
          <span class="title">消息通知</span>
          <el-button
            v-if="unreadCount > 0"
            type="primary"
            link
            size="small"
            @click.stop="markAllAsRead"
          >
            <el-icon class="button-icon"><Check /></el-icon>
            全部已读
          </el-button>
        </div>
        <div class="notification-list">
          <el-scrollbar max-height="400px">
            <div
              v-for="message in unreadMessageList"
              :key="message.id"
              class="notification-item"
              @click="markAsRead(message.id)"
            >
              <div class="message-icon">
                <el-icon>
                  <component :is="getMessageIcon(message.type)" />
                </el-icon>
              </div>
              <div class="message-content">
                <div class="message-title">{{ message.title }}</div>
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>

            <div v-if="unreadMessageList.length === 0" class="empty-message">
              <el-empty description="暂无消息" :image-size="80" />
            </div>
          </el-scrollbar>
        </div>
        <div class="notification-footer">
          <el-button type="primary" link @click="goToAllMessages">查看全部消息</el-button>
        </div>
      </div>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Check, InfoFilled, User, Document } from '@element-plus/icons-vue'
import type { ElDropdown } from 'element-plus'

defineOptions({ name: 'NotificationDropdown' })

const router = useRouter()
const notificationDropdownRef = ref<InstanceType<typeof ElDropdown>>()

// 模拟消息数据（你可以从 store 或 API 获取）
const messages = ref([
  {
    id: 1,
    type: 'system',
    title: '系统通知',
    content: '欢迎使用医疗质控系统',
    time: '刚刚',
    read: false,
  },
  {
    id: 2,
    type: 'user',
    title: '用户消息',
    content: '您有新的批次任务待处理',
    time: '5分钟前',
    read: false,
  },
])

const unreadCount = computed(() => {
  return messages.value.filter((msg) => !msg.read).length
})

const unreadMessageList = computed(() => {
  return messages.value.filter((msg) => !msg.read)
})

const getMessageIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    system: InfoFilled,
    user: User,
    default: Document,
  }
  return iconMap[type] || Document
}

const markAsRead = (id: number) => {
  const message = messages.value.find((msg) => msg.id === id)
  if (message) {
    message.read = true
  }
}

const markAllAsRead = () => {
  messages.value.forEach((msg) => {
    msg.read = true
  })
}

const goToAllMessages = () => {
  // 可以跳转到消息页面
  notificationDropdownRef.value?.handleClose()
}
</script>

<style scoped>
.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #606266;
  background: transparent;
}

.action-btn:hover {
  background: #f5f7fa;
  color: #409eff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.action-btn .el-icon {
  font-size: 1.25rem;
}

.notification-dropdown {
  width: 22rem;
  background: #ffffff;
}

.notification-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ebeef5;
}

.notification-header .title {
  font-size: 1rem;
  font-weight: 600;
  color: #303133;
}

.notification-header .button-icon {
  margin-right: 0.25rem;
}

.notification-list {
  max-height: 25rem;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 1rem;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-item .message-icon {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-item .message-icon .el-icon {
  font-size: 1rem;
}

.notification-item .message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.notification-item .message-content .message-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-item .message-content .message-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.notification-item .message-content .message-time {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.empty-message {
  padding: 2rem;
  text-align: center;
}

.notification-footer {
  padding: 1rem;
  border-top: 1px solid #ebeef5;
  text-align: center;
}
</style>

