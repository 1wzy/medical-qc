<template>
  <div class="api-test-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>后端连接测试</span>
        </div>
      </template>

      <el-space direction="vertical" size="large" style="width: 100%">
        <!-- 健康检查 -->
        <el-card shadow="hover">
          <template #header>
            <span>1. 健康检查</span>
          </template>
          <el-button type="primary" @click="testHealthCheck" :loading="healthLoading">
            测试健康检查接口
          </el-button>
          <div v-if="healthResult" class="result-box">
            <el-alert :type="healthResult.success ? 'success' : 'error'" :closable="false">
              <template #title>
                <div>
                  <div>状态: {{ healthResult.success ? '成功' : '失败' }}</div>
                  <div v-if="healthResult.data">响应: {{ JSON.stringify(healthResult.data) }}</div>
                  <div v-if="healthResult.error">错误: {{ healthResult.error }}</div>
                </div>
              </template>
            </el-alert>
          </div>
        </el-card>

        <!-- 获取规则列表 -->
        <el-card shadow="hover">
          <template #header>
            <span>2. 获取规则列表</span>
          </template>
          <el-button type="primary" @click="testGetRules" :loading="rulesLoading">
            测试获取规则列表
          </el-button>
          <div v-if="rulesResult" class="result-box">
            <el-alert :type="rulesResult.success ? 'success' : 'error'" :closable="false">
              <template #title>
                <div>
                  <div>状态: {{ rulesResult.success ? '成功' : '失败' }}</div>
                  <div v-if="rulesResult.data">
                    规则数量: {{ Array.isArray(rulesResult.data) ? rulesResult.data.length : 0 }}
                  </div>
                  <div v-if="rulesResult.error">错误: {{ rulesResult.error }}</div>
                  <div v-if="rulesResult.data && Array.isArray(rulesResult.data)" style="margin-top: 10px">
                    <el-collapse>
                      <el-collapse-item title="查看规则详情" :name="1">
                        <pre>{{ JSON.stringify(rulesResult.data, null, 2) }}</pre>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </div>
              </template>
            </el-alert>
          </div>
        </el-card>

        <!-- 连接信息 -->
        <el-card shadow="hover">
          <template #header>
            <span>连接信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="后端地址">http://127.0.0.1:8000</el-descriptions-item>
            <el-descriptions-item label="API 基础路径">/api</el-descriptions-item>
            <el-descriptions-item label="健康检查">/health</el-descriptions-item>
            <el-descriptions-item label="规则列表">/api/rules/</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { healthCheck, getRules } from '@/api/test'
import { ElMessage } from 'element-plus'

const healthLoading = ref(false)
const rulesLoading = ref(false)
const healthResult = ref<any>(null)
const rulesResult = ref<any>(null)

const testHealthCheck = async () => {
  healthLoading.value = true
  healthResult.value = null
  
  try {
    const response = await healthCheck()
    healthResult.value = {
      success: true,
      data: response.data,
    }
    ElMessage.success('健康检查成功！')
  } catch (error: any) {
    healthResult.value = {
      success: false,
      error: error.message || '连接失败，请检查后端是否运行',
    }
    ElMessage.error('健康检查失败！')
  } finally {
    healthLoading.value = false
  }
}

const testGetRules = async () => {
  rulesLoading.value = true
  rulesResult.value = null
  
  try {
    const data = await getRules()
    rulesResult.value = {
      success: true,
      data: data,
    }
    ElMessage.success('获取规则列表成功！')
  } catch (error: any) {
    rulesResult.value = {
      success: false,
      error: error.message || '获取规则列表失败',
    }
    ElMessage.error('获取规则列表失败！')
  } finally {
    rulesLoading.value = false
  }
}
</script>

<style scoped>
.api-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-box {
  margin-top: 15px;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}
</style>

