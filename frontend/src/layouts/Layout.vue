<template>
  <el-container class="layout-container">
    <!-- 左侧侧边栏 -->
    <el-aside class="aside" :width="isCollapse ? '64px' : '200px'">
      <div class="logo">
        {{ isCollapse ? 'M' : '医疗质控系统' }}
      </div>

      <el-menu
        router
        :default-active="route.path"
        :collapse="isCollapse"
        class="side-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>工作台</span>
        </el-menu-item>

        <el-sub-menu index="/rule">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>规则管理</span>
          </template>
          <el-menu-item index="/rule/manage">规则管理</el-menu-item>
          <el-menu-item index="/rule/set">规则集管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/data">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>数据管理</span>
          </template>
          <el-menu-item index="/data/basic">基础数据管理</el-menu-item>
          <el-menu-item index="/data/dataset">数据集管理</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/batches">
          <el-icon><Files /></el-icon>
          <span>批次管理</span>
        </el-menu-item>

        <el-menu-item index="/api-test">
          <el-icon><Tools /></el-icon>
          <span>API测试</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧 -->
    <el-container>
      <!-- 顶部 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>

          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbList"
              :key="item.path"
            >
              {{ item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <!-- 设置按钮 -->
            <el-tooltip content="系统设置" placement="bottom" effect="dark">
              <div class="action-btn" @click="handleSettings">
                <el-icon><Setting /></el-icon>
              </div>
            </el-tooltip>

            <!-- 全屏按钮 -->
            <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏'" placement="bottom" effect="dark">
              <div class="action-btn" @click="toggleFullscreen">
                <el-icon>
                  <Expand v-if="!isFullscreen" />
                  <Fold v-else />
                </el-icon>
              </div>
            </el-tooltip>

            <!-- 国际化 -->
            <I18nDropdown />

            <!-- 消息通知 -->
            <NotificationDropdown />
          </div>

          <!-- 用户下拉菜单 -->
          <UserDropdown />
        </div>
      </el-header>

      <!-- Tabs -->
      <TabsView />

      <!-- 主内容 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataAnalysis, Fold, Expand, User, ArrowDown, SwitchButton, Folder, Files, Tools, Monitor, Setting } from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'
import { ElMessage } from 'element-plus'
import NotificationDropdown from '@/components/NotificationDropdown.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import I18nDropdown from '@/components/I18nDropdown.vue'
import TabsView from '@/components/TabsView.vue'
import { useFullscreen } from '@vueuse/core'
import { getRouteIcon } from '@/utils/routeIcons'

defineOptions({
  name: 'AppLayout'
})

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

const isCollapse = ref(false)

// 全屏功能
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen()

// 获取用户名
const username = computed(() => {
  return localStorage.getItem('username') || '用户'
})

// 处理设置按钮
const handleSettings = () => {
  ElMessage.info('系统设置功能开发中')
}

const breadcrumbMap: Record<string, { name: string; parent?: string }> = {
  '/dashboard': { name: '工作台' },
  '/rule/manage': { name: '规则管理', parent: '/rule' },
  '/rule/set': { name: '规则集管理', parent: '/rule' },
  '/rule': { name: '规则管理' },
  '/data/basic': { name: '基础数据管理', parent: '/data' },
  '/data/dataset': { name: '数据集管理', parent: '/data' },
  '/data': { name: '数据管理' },
  '/batches': { name: '批次管理' },
  '/api-test': { name: 'API测试' }
}

const breadcrumbList = computed(() => {
  let path = route.path
  let current = breadcrumbMap[path]
  
  // 处理动态路由 /data/basic/:id
  if (path.startsWith('/data/basic/') && path !== '/data/basic') {
    const dataId = path.split('/').pop()
    current = { name: `数据详情 (ID: ${dataId})`, parent: '/data/basic' }
  }
  
  // 处理动态路由 /data/dataset/:id
  if (path.startsWith('/data/dataset/') && path !== '/data/dataset') {
    const datasetId = path.split('/').pop()
    current = { name: `数据集详情 (ID: ${datasetId})`, parent: '/data/dataset' }
  }
  
  // 处理动态路由 /batches/:id
  if (path.startsWith('/batches/') && path !== '/batches') {
    const batchId = path.split('/').pop()
    current = { name: `批次详情 (ID: ${batchId})`, parent: '/batches' }
  }
  
  if (!current) return []

  const list = [{ name: current.name, path: route.path }]
  if (current.parent) {
    const parent = breadcrumbMap[current.parent]
    if (parent) list.unshift({ name: parent.name, path: current.parent }) 
  }
  return list
})

watch(
  () => route.path,
  (path) => {
    let title = breadcrumbMap[path]?.name
    
    // 处理动态路由 /data/basic/:id
    if (!title && path.startsWith('/data/basic/') && path !== '/data/basic') {
      const dataId = path.split('/').pop()
      title = `数据详情 (ID: ${dataId})`
    }
    
    // 处理动态路由 /data/dataset/:id
    if (!title && path.startsWith('/data/dataset/') && path !== '/data/dataset') {
      const datasetId = path.split('/').pop()
      title = `数据集详情 (ID: ${datasetId})`
    }
    
    // 处理动态路由 /batches/:id
    if (!title && path.startsWith('/batches/') && path !== '/batches') {
      const batchId = path.split('/').pop()
      title = `批次详情 (ID: ${batchId})`
    }
    
    if (!title) {
      title = path.slice(1) || '首页'
    }
    
    tabsStore.addTab({
      path,
      title,
      icon: getRouteIcon(path),
      closable: path !== '/dashboard' // 只有工作台不可关闭
    })
  },
  { immediate: true }
)

const handleMenuSelect = (index: string) => {
  // 确保路由跳转正确执行
  router.push(index).catch((err) => {
    // 忽略重复导航错误
    if (err.name !== 'NavigationDuplicated') {
      console.error('菜单导航失败:', err)
    }
  })
}
</script>

<style scoped>
/* ===== 整体背景 ===== */
.layout-container {
  height: 100vh;
  background: #f4f6f9;
}

/* ===== 侧边栏（白色 + 阴影） ===== */

.aside {
  background: #ffffff;
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* ===== Logo 区 ===== */
.logo {
  height: 56px;
  background: linear-gradient(135deg, #4f8df7, #6aa6ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
}

/* ===== 菜单 ===== */
.side-menu {
  border-right: none;
  background: transparent;
}

/* 菜单文字 */
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: #303133;
  font-size: 14px;
}

/* 子菜单项统一样式，避免激活时位移 */
:deep(.el-sub-menu .el-menu-item) {
  padding-left: 50px !important;
  margin: 4px 8px;
  width: calc(100% - 16px);
  box-sizing: border-box;
}

/* hover */
:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: #f2f6fc;
}

/* 选中项 - 保持与普通项完全相同的布局属性，只改变颜色和背景 */
:deep(.el-sub-menu .el-menu-item.is-active) {
  background: #e8f0ff;
  color: #409eff;
  border-radius: 6px;
  margin: 4px 8px;
  padding-left: 50px !important;
  width: calc(100% - 16px);
  box-sizing: border-box;
}

/* ===== 顶部 Header ===== */
.header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #ffffff;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  padding-left: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 16px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 16px;
  border-right: 1px solid #ebeef5;
}

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

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
  color: #606266;
  font-size: 14px;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-weight: 500;
}

.arrow-down {
  font-size: 12px;
  transition: transform 0.3s;
}

.collapse-btn {
  cursor: pointer;
  font-size: 18px;
  color: #606266;
}

/* ===== 主内容区域 ===== */
.main {
  padding: 20px;
  background: #f4f6f9;
}
</style>

