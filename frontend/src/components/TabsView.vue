<template>
  <div class="tabs-container">
    <div class="tabs-left-icon" @click="slideLeft">
      <el-icon><ArrowLeft /></el-icon>
    </div>
    <div class="tabs-pages" ref="tabsPagesRef">
      <div
        class="tabs-page-item"
        :class="{ active: tab.path === tabsStore.activePath }"
        v-for="tab in tabsStore.tabs"
        :key="tab.path"
        :ref="(el) => setTabRef(el, tab.path)"
        @click="navigation(tab.path)"
      >
        <el-icon v-if="tab.icon" class="tabs-page-icon" :size="18">
          <component :is="getIconComponent(tab.icon)" />
        </el-icon>
        <div>{{ tab.title }}</div>
        <el-icon v-if="tab.closable" class="close-icon" @click.stop="handleClose(tab)">
          <Close />
        </el-icon>
      </div>
    </div>
    <div class="tabs-right-icon" @click="slideRight">
      <el-icon><ArrowRight /></el-icon>
    </div>
    <div class="tabs-dropdown">
      <el-dropdown trigger="click" class="tabs-dropdown-wrapper">
        <div class="tabs-dropdown-icon">
          <el-icon><MoreFilled /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="tabsStore.closeOtherTabs(tabsStore.activePath)">
              <el-icon><Minus /></el-icon>
              <span>关闭其他标签页</span>
            </el-dropdown-item>
            <el-dropdown-item @click="handleCloseAll">
              <el-icon><Delete /></el-icon>
              <span>关闭所有标签页</span>
            </el-dropdown-item>
            <el-dropdown-item @click="tabsStore.closeRightTabs(tabsStore.activePath)">
              <el-icon><DArrowRight /></el-icon>
              <span>关闭右侧标签页</span>
            </el-dropdown-item>
            <el-dropdown-item @click="tabsStore.closeLeftTabs(tabsStore.activePath)">
              <el-icon><DArrowLeft /></el-icon>
              <span>关闭左侧标签页</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  ArrowRight,
  Close,
  MoreFilled,
  Minus,
  Delete,
  DArrowRight,
  DArrowLeft,
  Monitor,
  Setting,
  List,
  Folder,
  Files,
  Tools,
} from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'
import type { TabItem } from '@/stores/tabs'

defineOptions({ name: 'TabsView' })

const router = useRouter()
const tabsStore = useTabsStore()
const tabsPagesRef = ref<HTMLDivElement>()

// 存储每个标签页的 DOM 引用
const tabRefs = new Map<string, HTMLDivElement>()

// 图标映射
const iconMap: Record<string, any> = {
  Monitor,
  Setting,
  List,
  Folder,
  Files,
  Tools,
}

// 获取图标组件
const getIconComponent = (iconName?: string) => {
  if (!iconName) return Monitor
  return iconMap[iconName] || Monitor
}

// 设置标签页引用
const setTabRef = (el: Element | ComponentPublicInstance | null, path: string) => {
  if (el && el instanceof HTMLElement) {
    tabRefs.set(path, el as HTMLDivElement)
  } else {
    tabRefs.delete(path)
  }
}

// 滚动到选中的标签页
const scrollToActiveTab = () => {
  nextTick(() => {
    const activeTab = tabRefs.get(tabsStore.activePath)
    const container = tabsPagesRef.value
    if (!activeTab || !container) return

    const containerRect = container.getBoundingClientRect()
    const tabRect = activeTab.getBoundingClientRect()

    // 检查标签页是否在可视区域内
    const isVisible = tabRect.left >= containerRect.left && tabRect.right <= containerRect.right

    if (!isVisible) {
      // 如果标签页在左侧不可见
      if (tabRect.left < containerRect.left) {
        container.scrollTo({
          left: container.scrollLeft + (tabRect.left - containerRect.left) - 10,
          behavior: 'smooth',
        })
      }
      // 如果标签页在右侧不可见
      else if (tabRect.right > containerRect.right) {
        container.scrollTo({
          left: container.scrollLeft + (tabRect.right - containerRect.right) + 10,
          behavior: 'smooth',
        })
      }
    }
  })
}

// 监听 activePath 变化，自动滚动到选中的标签页
watch(
  () => tabsStore.activePath,
  () => {
    scrollToActiveTab()
  },
  { immediate: true },
)

// 监听 tabs 数组变化，确保在标签页添加或删除后也能正确滚动
watch(
  () => tabsStore.tabs.length,
  () => {
    scrollToActiveTab()
  },
)

// 导航到指定路径
const navigation = (path: string) => {
  router.push(path).catch((err) => {
    if (err.name !== 'NavigationDuplicated') {
      console.error('路由跳转失败:', err)
    }
  })
  tabsStore.setActive(path)
  scrollToActiveTab()
}

// 关闭标签页
const handleClose = (item: TabItem) => {
  tabsStore.removeTab(item.path)
  router.push(tabsStore.activePath).catch((err) => {
    if (err.name !== 'NavigationDuplicated') {
      console.error('路由跳转失败:', err)
    }
  })
  scrollToActiveTab()
}

// 关闭所有标签页
const handleCloseAll = () => {
  tabsStore.closeAllTabs()
  if (tabsStore.activePath) {
    router.push(tabsStore.activePath).catch((err) => {
      if (err.name !== 'NavigationDuplicated') {
        console.error('路由跳转失败:', err)
      }
    })
  }
}

// 滚动步进值（容器宽度的80%）
const SCROLL_STEP_RATIO = 0.8

// 获取滚动容器信息
const getScrollInfo = () => {
  const container = tabsPagesRef.value
  if (!container) return null

  return {
    container,
    containerWidth: container.offsetWidth,
    contentWidth: container.scrollWidth,
    scrollLeft: container.scrollLeft,
    maxScrollLeft: container.scrollWidth - container.offsetWidth,
  }
}

// 向左滑动
const slideLeft = () => {
  const info = getScrollInfo()
  if (!info) return

  // 检查是否需要滚动（内容超出容器）
  if (info.containerWidth >= info.contentWidth) return

  // 计算滚动距离（容器宽度的80%）
  const scrollDistance = info.containerWidth * SCROLL_STEP_RATIO

  // 计算目标滚动位置
  const targetScrollLeft = Math.max(0, info.scrollLeft - scrollDistance)

  // 如果已经在最左边，不执行滚动
  if (info.scrollLeft <= 0) return

  info.container.scrollTo({
    left: targetScrollLeft,
    behavior: 'smooth',
  })
}

// 向右滑动
const slideRight = () => {
  const info = getScrollInfo()
  if (!info) return

  // 检查是否需要滚动（内容超出容器）
  if (info.containerWidth >= info.contentWidth) return

  // 计算滚动距离（容器宽度的80%）
  const scrollDistance = info.containerWidth * SCROLL_STEP_RATIO

  // 计算目标滚动位置
  const targetScrollLeft = Math.min(info.maxScrollLeft, info.scrollLeft + scrollDistance)

  // 如果已经在最右边，不执行滚动
  if (info.scrollLeft >= info.maxScrollLeft) return

  info.container.scrollTo({
    left: targetScrollLeft,
    behavior: 'smooth',
  })
}
</script>

<style scoped>
.tabs-container {
  padding-top: 4px;
  height: 40px;
  padding-left: 12px;
  padding-right: 16px;
  display: flex;
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #ebeef5;
}

.tabs-left-icon {
  padding: 0;
  height: 100%;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
  flex-shrink: 0;
}

.tabs-right-icon {
  padding: 0 8px;
  height: 100%;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
  flex-shrink: 0;
}

.tabs-left-icon:hover,
.tabs-right-icon:hover {
  color: #409eff;
}

.tabs-pages {
  padding: 0 12px 0 0;
  height: 40px;
  flex: 1;
  display: flex;
  font-size: 14px;
  overflow-x: auto;
  gap: 4px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tabs-pages::-webkit-scrollbar {
  display: none;
}

.tabs-page-item {
  padding: 0 12px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s;
  position: relative;
}

.tabs-page-item:hover {
  background-color: #f5f7fa;
  color: #303133;
}

.tabs-page-item.active {
  background-color: rgba(64, 158, 255, 0.2);
  color: #409eff;
  font-weight: 600;
}

.tabs-page-icon {
  flex-shrink: 0;
}

.close-icon {
  margin-left: 4px;
  font-size: 12px;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
  color: #909399;
  cursor: pointer;
}

.close-icon:hover {
  background-color: #f56c6c;
  color: #ffffff;
  transform: scale(1.1);
}

.tabs-dropdown {
  height: 100%;
  margin-right: 8px;
}

.tabs-dropdown-wrapper {
  height: 100%;
  cursor: pointer;
}

.tabs-dropdown-icon {
  padding: 0 8px;
  display: flex;
  align-items: center;
  color: #606266;
  transition: color 0.3s;
}

.tabs-dropdown-icon:hover {
  color: #409eff;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  transition: background-color 0.2s, color 0.2s;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f5f7fa !important;
  color: #409eff;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}
</style>

