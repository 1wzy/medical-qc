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
        <el-sub-menu index="/rule">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>规则管理</span>
          </template>
          <el-menu-item index="/rule/manage">规则管理</el-menu-item>
          <el-menu-item index="/rule/set">规则集管理</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/upload">
          <el-icon><Document /></el-icon>
          <span>文书上传</span>
        </el-menu-item>

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
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span class="username">{{ username }}</span>
              <el-icon class="arrow-down"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  <span style="margin-left: 8px">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Tabs -->
      <div class="tabs-bar">
        <el-tabs
          v-model="tabsStore.activePath"
          type="card"
          closable
          @tab-click="onTabClick"
          @tab-remove="onTabRemove"
        >
          <el-tab-pane
            v-for="tab in tabsStore.tabs"
            :key="tab.path"
            :name="tab.path"
            :label="tab.title"
            :closable="tab.closable"
          />
        </el-tabs>
      </div>

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
import { DataAnalysis, Fold, Expand, User, ArrowDown, SwitchButton, Document, Files, Tools } from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'
import { ElMessage } from 'element-plus'

defineOptions({
  name: 'AppLayout'
})

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

const isCollapse = ref(false)

// 获取用户名
const username = computed(() => {
  return localStorage.getItem('username') || '用户'
})

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  if (command === 'logout') {
    handleLogout()
  }
}

// 登出功能
const handleLogout = () => {
  // 清除登录状态
  localStorage.removeItem('isLoggedIn')
  localStorage.removeItem('username')
  
  // 清除标签页状态
  tabsStore.tabs = [
    {
      path: '/rule/manage',
      title: '规则管理',
      closable: false,
    },
  ]
  tabsStore.activePath = '/rule/manage'
  
  ElMessage.success('已退出登录')
  
  // 跳转到登录页
  router.push('/').catch((err) => {
    if (err.name !== 'NavigationDuplicated') {
      console.error('路由跳转失败:', err)
    }
  })
}

const breadcrumbMap: Record<string, { name: string; parent?: string }> = {
  '/rule/manage': { name: '规则管理', parent: '/rule' },
  '/rule/set': { name: '规则集管理', parent: '/rule' },
  '/rule': { name: '规则管理' },
  '/upload': { name: '文书上传' },
  '/batches': { name: '批次管理' },
  '/api-test': { name: 'API测试' }
}

const breadcrumbList = computed(() => {
  const current = breadcrumbMap[route.path]
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
    const title = breadcrumbMap[path]?.name || path.slice(1)
    tabsStore.addTab({
      path,
      title,
      closable: path !== '/rules'
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

interface TabPane {
  paneName?: string
  name?: string
}

const onTabClick = (pane: TabPane) => {
  const targetPath = pane.paneName || pane.name
  if (targetPath) {
    router.push(targetPath).catch((err) => {
      if (err.name !== 'NavigationDuplicated') {
        console.error('Tab导航失败:', err)
      }
    })
  }
}

const onTabRemove = (path: string) => {
  tabsStore.removeTab(path)
  if (tabsStore.activePath) {
    router.push(tabsStore.activePath).catch((err) => {
      if (err.name !== 'NavigationDuplicated') {
        console.error('Tab删除后导航失败:', err)
      }
    })
  }
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
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
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

/* ===== Tabs 栏 ===== */
.tabs-bar {
  padding: 6px 12px 0;
  background: #ffffff;
  border-bottom: 1px solid #ebeef5;
}

/* Tabs 容器 - 移除所有边框 */
:deep(.el-tabs--card > .el-tabs__header) {
  border-bottom: none;
  border: none;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__nav) {
  border: none;
}

/* 单个 Tab - 移除边框 */
:deep(.el-tabs__item) {
  height: 36px;
  line-height: 36px;
  border-radius: 8px 8px 0 0;
  margin-right: 6px;
  background: #f5f7fa;
  color: #606266;
  border: none !important;
  border-bottom: none !important;
}

/* 激活 Tab - 使用和侧边栏菜单项相同的浅蓝色背景 */
:deep(.el-tabs__item.is-active) {
  background: #e8f0ff;
  color: #409eff;
  font-weight: 500;
  border: none !important;
  border-bottom: none !important;
}

/* ===== 主内容区域 ===== */
.main {
  padding: 20px;
  background: #f4f6f9;
}
</style>

