import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface TabItem {
  path: string
  title: string
  closable: boolean
}

export const useTabsStore = defineStore('tabs', () => {
  // 当前激活的标签
  const activePath = ref('/rules')

  // 标签列表
  const tabs = ref<TabItem[]>([
    {
      path: '/rules',
      title: '规则管理',
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

    tabs.value.splice(index, 1)

    // 如果删除的是当前激活页，自动切换
    if (activePath.value === path) {
      const next = tabs.value[index - 1] || tabs.value[0]
      if (next) {
        activePath.value = next.path
      }
    }
  }

  function setActive(path: string) {
    activePath.value = path
  }

  return {
    tabs,
    activePath,
    addTab,
    removeTab,
    setActive,
  }
})
