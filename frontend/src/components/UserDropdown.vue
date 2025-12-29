<template>
  <el-dropdown @command="handleCommand" trigger="click" placement="bottom-end">
    <div class="user-card">
      <div class="avatar-wrapper">
        <div class="user-avatar">
          <el-icon :size="36"><User /></el-icon>
        </div>
        <span class="status-badge"></span>
      </div>
      <div class="user-info">
        <span class="username ellipsis-text">{{ username }}</span>
        <span class="user-role-badge ellipsis-text">管理员</span>
      </div>
      <el-icon class="arrow-icon">
        <ArrowDown />
      </el-icon>
    </div>
    <template #dropdown>
      <div class="user-menu-wrapper">
        <!-- 用户信息头部 -->
        <div class="user-header">
          <div class="avatar-wrapper">
            <div class="header-avatar">
              <el-icon :size="48"><User /></el-icon>
            </div>
            <span class="status-badge"></span>
          </div>
          <div class="user-info">
            <div class="name-row">
              <span class="user-name ellipsis-text">{{ username }}</span>
              <span class="pro-badge ellipsis-text">管理员</span>
            </div>
            <div class="user-email">{{ userEmail }}</div>
          </div>
        </div>

        <!-- 菜单项 -->
        <el-dropdown-menu class="user-menu">
          <el-dropdown-item command="profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-dropdown-item>
          <el-dropdown-item command="settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-dropdown-item>
          <el-dropdown-item divided command="logout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </div>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineOptions({ name: 'UserDropdown' })

const router = useRouter()

const username = computed(() => {
  return localStorage.getItem('username') || '用户'
})

const userEmail = computed(() => {
  return localStorage.getItem('email') || 'user@example.com'
})

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人中心
      ElMessage.info('个人中心功能开发中')
      break
    case 'settings':
      // 跳转到系统设置
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  // 清除登录状态
  localStorage.removeItem('isLoggedIn')
  localStorage.removeItem('username')
  localStorage.removeItem('email')
  
  ElMessage.success('已退出登录')
  
  // 跳转到登录页
  router.push('/').catch((err) => {
    if (err.name !== 'NavigationDuplicated') {
      console.error('路由跳转失败:', err)
    }
  })
}
</script>

<style scoped>
.user-card {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 4px 8px 4px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-card:hover {
  background-color: #f5f7fa;
}

.user-card:hover .arrow-icon {
  color: #409eff;
}

.user-card .avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.user-card .avatar-wrapper .status-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: #52c41a;
  border: 2px solid #ffffff;
  border-radius: 50%;
}

.user-card .user-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 4px;
}

.user-card .user-info .username {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
  max-width: 100px;
}

.user-card .user-info .user-role-badge {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  font-size: 11px;
  font-weight: 500;
  border-radius: 10px;
  border: 1px solid rgba(64, 158, 255, 0.2);
  white-space: nowrap;
  line-height: 1.2;
  max-width: 100px;
}

.user-card .arrow-icon {
  font-size: 1rem;
  color: #606266;
  transition: color 0.2s;
  margin-left: 4px;
}

.user-menu-wrapper {
  margin-top: 8px;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  background: #ffffff;
}

.user-header .avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.user-header .avatar-wrapper .status-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  background: #52c41a;
  border: 2px solid #ffffff;
  border-radius: 50%;
}

.user-header .user-info {
  flex: 1;
  min-width: 0;
}

.user-header .user-info .name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.user-header .user-info .name-row .user-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
  max-width: 100px;
}

.user-header .user-info .name-row .pro-badge {
  display: inline-block;
  padding: 3px 10px;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  font-size: 11px;
  font-weight: 500;
  border-radius: 12px;
  line-height: 1.2;
  border: 1px solid rgba(64, 158, 255, 0.2);
  max-width: 100px;
}

.user-header .user-info .user-email {
  font-size: 13px;
  color: #606266;
  opacity: 0.8;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.avatar-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-wrapper .user-avatar,
.avatar-wrapper .header-avatar {
  border-radius: 50%;
  overflow: hidden;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-wrapper .user-avatar {
  width: 36px;
  height: 36px;
}

.avatar-wrapper .header-avatar {
  width: 48px;
  height: 48px;
}

.ellipsis-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.user-menu) {
  padding: 4px 0;
  min-width: 200px;
  background: #ffffff;
}

:deep(.user-menu .el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  transition: background-color 0.2s;
  background: transparent;
}

:deep(.user-menu .el-dropdown-menu__item:hover) {
  background: #f5f7fa;
  color: #409eff;
}

:deep(.user-menu .el-dropdown-menu__item .el-icon) {
  font-size: 1.25rem;
  flex-shrink: 0;
}

:deep(.user-menu .el-dropdown-menu__item span) {
  font-size: 14px;
  flex: 1;
}
</style>

