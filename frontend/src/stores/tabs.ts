import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface TabItem {
  path: string
  title: string
  icon?: string
  closable: boolean
}

export const useTabsStore = defineStore('tabs', () => {
  // 当前激活的标签
  const activePath = ref('/dashboard')

  // 标签列表
  const tabs = ref<TabItem[]>([
    {
      path: '/dashboard',
      title: '工作台',
      icon: 'Monitor',
      closable: false, // 首页不可关闭
    },
  ])

  function addTab(tab: TabItem) {
    if (!tabs.value.find(t => t.path === tab.path)) {
      tabs.value.push(tab)
    }
    activePath.value = tab.path
  }

  function removeTab(path: string) {
    const index = tabs.value.findIndex(t => t.path === path)
    if (index === -1) return

    const isActive = tabs.value[index]?.path === activePath.value
    tabs.value.splice(index, 1)

    // 如果删除的是当前激活页，自动切换
    if (isActive && tabs.value.length > 0) {
      // 优先跳转到右侧的标签页，如果没有则跳转到左侧
      const nextTab = tabs.value[index] || tabs.value[index - 1]
      if (nextTab) {
        activePath.value = nextTab.path
      }
    }
    
    // 如果只剩一个标签页，设置为不可关闭
    if (tabs.value.length === 1) {
      tabs.value[0]!.closable = false
    }
  }

  function setActive(path: string) {
    activePath.value = path
  }

  function updateTabTitle(path: string, title: string) {
    const tab = tabs.value.find(t => t.path === path)
    if (tab) {
      tab.title = title
    }
  }

  /**
   * 关闭其他标签页
   * @param path 保留的标签页路径
   */
  function closeOtherTabs(path: string) {
    tabs.value = tabs.value.filter((tab) => tab.path === path || !tab.closable)
    activePath.value = path
  }

  /**
   * 关闭所有标签页（保留不可关闭的）
   */
  function closeAllTabs() {
    tabs.value = tabs.value.filter((tab) => !tab.closable)
    if (tabs.value.length > 0) {
      activePath.value = tabs.value[0]?.path || ''
    }
  }

  /**
   * 关闭左侧标签页
   * @param path 当前标签页路径
   */
  function closeLeftTabs(path: string) {
    const index = tabs.value.findIndex((tab) => tab.path === path)
    if (index === -1) return

    // 保留当前标签页及右侧的标签页，以及不可关闭的标签页
    tabs.value = tabs.value.filter((tab, i) => i >= index || !tab.closable)
    activePath.value = path
  }

  /**
   * 关闭右侧标签页
   * @param path 当前标签页路径
   */
  function closeRightTabs(path: string) {
    const index = tabs.value.findIndex((tab) => tab.path === path)
    if (index === -1) return

    // 保留当前标签页及左侧的标签页，以及不可关闭的标签页
    tabs.value = tabs.value.filter((tab, i) => i <= index || !tab.closable)
    activePath.value = path
  }

  return {
    tabs,
    activePath,
    addTab,
    removeTab,
    setActive,
    updateTabTitle,
    closeOtherTabs,
    closeAllTabs,
    closeLeftTabs,
    closeRightTabs,
  }
})
