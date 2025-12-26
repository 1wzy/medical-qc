<template>
  <div class="upload-page">
    <el-card class="upload-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">文书上传</div>
            <div class="subtitle">支持批量上传病历文书，系统将自动生成质控批次</div>
          </div>
          <el-button type="primary" :disabled="fileList.length === 0" @click="handleSubmit">
            提交上传
          </el-button>
        </div>
      </template>

      <!-- 批次信息 -->
      <el-form :model="form" label-width="90px" class="batch-form" :inline="false">
        <el-form-item label="批次名称">
          <el-input
            v-model="form.batchName"
            placeholder="如：2025-12-住院病历抽检批次"
          />
        </el-form-item>
        <el-form-item label="科室">
          <el-select v-model="form.department" placeholder="请选择科室" clearable>
            <el-option label="全部科室" value="all" />
            <el-option label="内科" value="internal" />
            <el-option label="外科" value="surgery" />
            <el-option label="急诊科" value="emergency" />
            <el-option label="ICU" value="icu" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注说明">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="2"
            placeholder="可填写本次上传的来源、抽检规则等说明，便于后续追溯"
          />
        </el-form-item>
      </el-form>

      <!-- 上传区域 -->
      <el-divider>文书文件</el-divider>

      <el-upload
        class="upload-area"
        drag
        multiple
        :auto-upload="false"
        :file-list="fileList"
        :on-change="handleChange"
        :on-remove="handleRemove"
        :limit="50"
        :on-exceed="handleExceed"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
        <div class="el-upload__tip">
          支持 PDF、Word、Excel 等常见文书格式，单个文件不超过 50MB
        </div>
      </el-upload>

      <!-- 预览列表 -->
      <el-table
        v-if="fileList.length > 0"
        :data="fileList"
        size="small"
        class="file-table"
        border
      >
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="name" label="文件名" min-width="260" show-overflow-tooltip />
        <el-table-column prop="size" label="大小" width="120" align="center">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'ready'">待上传</el-tag>
            <el-tag v-else-if="row.status === 'success'" type="success">已上传</el-tag>
            <el-tag v-else-if="row.status === 'error'" type="danger">失败</el-tag>
            <el-tag v-else type="info">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { UploadFile, UploadProps } from 'element-plus'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

interface UploadForm {
  batchName: string
  department: string
  remark: string
}

const form = reactive<UploadForm>({
  batchName: '',
  department: 'all',
  remark: ''
})

const fileList = ref<UploadFile[]>([])

const handleChange: UploadProps['onChange'] = (file, files) => {
  fileList.value = files
}

const handleRemove: UploadProps['onRemove'] = (file, files) => {
  if (files) {
    fileList.value = files
  }
}

const handleExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('单次最多上传 50 个文件')
}

const formatSize = (size?: number) => {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

const handleSubmit = () => {
  if (!form.batchName.trim()) {
    ElMessage.warning('请先填写批次名称')
    return
  }
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的文书文件')
    return
  }

  // 这里预留真实上传接口调用位置
  // TODO: 调用后端 API 提交 form + fileList
  ElMessage.success(`已提交 ${fileList.value.length} 个文件进行上传（模拟）`)
}
</script>

<style scoped>
.upload-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.upload-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.batch-form {
  margin-bottom: 12px;
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 40px;
  color: #409eff;
  margin-bottom: 8px;
}

.file-table {
  margin-top: 16px;
}
</style>


