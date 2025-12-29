<template>
  <el-dropdown trigger="click" placement="bottom-end">
    <div class="action-btn">
      <el-icon><Setting /></el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          :class="{ 'is-active': currentLanguage === 'CN' }"
          @click="currentLanguage = 'CN'"
        >
          <span class="language-code">CN</span>
          <span class="language-name">简体中文</span>
        </el-dropdown-item>
        <el-dropdown-item
          :class="{ 'is-active': currentLanguage === 'EN' }"
          @click="currentLanguage = 'EN'"
        >
          <span class="language-code">EN</span>
          <span class="language-name">English</span>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Setting } from '@element-plus/icons-vue'

defineOptions({ name: 'I18nDropdown' })

const currentLanguage = ref<string>('CN')
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

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.25rem;
  padding: 12px 20px;
  transition: background-color 0.2s, color 0.2s;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f5f7fa !important;
  color: #409eff;
}

:deep(.el-dropdown-menu__item.is-active) {
  background: #f5f7fa !important;
  color: #409eff;
}

:deep(.el-dropdown-menu__item.is-active .language-code) {
  color: #409eff;
  font-weight: 700;
}

:deep(.el-dropdown-menu__item.is-active .language-name) {
  color: #409eff;
  font-weight: 600;
}

.language-code {
  font-size: 13px;
  letter-spacing: 0.5px;
  min-width: 32px;
}

.language-name {
  font-size: 14px;
  flex: 1;
}

:deep(.el-dropdown-menu__item:hover .language-code),
:deep(.el-dropdown-menu__item:hover .language-name) {
  color: #409eff;
}
</style>

