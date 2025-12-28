<template>
  <div class="dataset-page">
    <el-card class="dataset-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div>
            <div class="title">数据集管理</div>
            <div class="subtitle">创建和管理数据集，支持导入JSON文件或从基础数据中选择</div>
          </div>
          <el-button type="primary" @click="handleCreateDataset">
            创建数据集
          </el-button>
        </div>
      </template>

      <!-- 数据集列表 -->
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索数据集名称"
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table
        v-loading="loading"
        :data="filteredDatasetList"
        size="small"
        class="dataset-table"
        border
      >
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="name" label="数据集名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="data_count" label="数据条数" width="120" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180" align="center" />
        <el-table-column label="操作" width="250" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑数据集对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="datasetForm" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="datasetForm.name" placeholder="请输入数据集名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="datasetForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入数据集描述"
          />
        </el-form-item>
        
        <el-form-item label="数据来源">
          <el-radio-group v-model="dataSource" @change="handleDataSourceChange">
            <el-radio label="upload">上传JSON文件</el-radio>
            <el-radio label="select">从基础数据选择</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 上传JSON文件 -->
        <el-form-item v-if="dataSource === 'upload'" label="JSON文件">
          <el-upload
            class="upload-area"
            drag
            :auto-upload="false"
            :file-list="uploadFileList"
            :on-change="handleUploadChange"
            :on-remove="handleUploadRemove"
            accept=".json"
            :limit="1"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将JSON文件拖到此处，或 <em>点击上传</em>
            </div>
            <div class="el-upload__tip">
              仅支持 JSON 格式文件，单个文件不超过 50MB
            </div>
          </el-upload>
        </el-form-item>

        <!-- 从基础数据选择 -->
        <el-form-item v-if="dataSource === 'select'" label="选择数据">
          <div class="select-toolbar">
            <el-input
              v-model="basicDataSearchKeyword"
              placeholder="搜索基础数据"
              clearable
              style="width: 300px"
              @input="handleBasicDataSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="small" @click="handleSelectAll">全选</el-button>
            <el-button size="small" @click="handleClearSelection">清空</el-button>
          </div>
          <el-table
            ref="basicDataTableRef"
            v-loading="basicDataLoading"
            :data="filteredBasicDataList"
            size="small"
            class="select-table"
            border
            max-height="300"
            @selection-change="handleBasicDataSelectionChange"
          >
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column type="index" label="#" width="60" align="center" />
            <el-table-column prop="id" label="数据ID" width="120" show-overflow-tooltip />
            <el-table-column prop="file_name" label="文件名" min-width="260" show-overflow-tooltip />
            <el-table-column prop="file_size" label="大小" width="120" align="center">
              <template #default="{ row }">
                {{ formatSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="上传时间" width="180" align="center" />
          </el-table>
          <div class="selected-count">
            已选择 {{ selectedBasicData.length }} 条数据
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDataset">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { UploadFile, UploadProps, FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Search } from '@element-plus/icons-vue'
import {
  getDatasetList,
  getDataset,
  createDataset,
  updateDataset,
  deleteDataset,
  uploadDataset,
  getBasicDataList,
  type Dataset,
  type BasicData
} from '@/api/data'

const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('创建数据集')
const dataSource = ref<'upload' | 'select'>('upload')
const uploadFileList = ref<UploadFile[]>([])
const basicDataSearchKeyword = ref('')
const selectedBasicData = ref<BasicData[]>([])
const basicDataList = ref<BasicData[]>([])
const basicDataLoading = ref(false)
const formRef = ref<FormInstance>()
const basicDataTableRef = ref()

const datasetList = ref<Dataset[]>([])

// 加载数据集列表
const loadDatasetList = async () => {
  loading.value = true
  try {
    const response = await getDatasetList({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchKeyword.value || undefined
    })
    datasetList.value = response.items
    total.value = response.total
  } catch (error: any) {
    ElMessage.error('加载数据集失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 加载基础数据列表（用于选择）
const loadBasicDataList = async () => {
  basicDataLoading.value = true
  try {
    const response = await getBasicDataList({
      skip: 0,
      limit: 1000, // 加载所有基础数据供选择
      search: basicDataSearchKeyword.value || undefined
    })
    basicDataList.value = response.items
  } catch (error: any) {
    ElMessage.error('加载基础数据失败: ' + (error.message || '未知错误'))
  } finally {
    basicDataLoading.value = false
  }
}

// 初始化加载
onMounted(() => {
  loadDatasetList()
})

const datasetForm = reactive<{
  id?: number
  name: string
  description: string
}>({
  name: '',
  description: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' }
  ]
}

const filteredDatasetList = computed(() => {
  // 后端已处理搜索
  return datasetList.value
})

const filteredBasicDataList = computed(() => {
  // 后端已处理搜索
  return basicDataList.value
})

const handleSearch = () => {
  currentPage.value = 1
  loadDatasetList()
}

const handleBasicDataSearch = () => {
  loadBasicDataList()
}

const handleCreateDataset = () => {
  dialogTitle.value = '创建数据集'
  datasetForm.id = undefined
  datasetForm.name = ''
  datasetForm.description = ''
  dataSource.value = 'upload'
  uploadFileList.value = []
  selectedBasicData.value = []
  basicDataList.value = []
  basicDataSearchKeyword.value = ''
  dialogVisible.value = true
  // 如果选择从基础数据选择，加载基础数据列表
  if (dataSource.value === 'select') {
    loadBasicDataList()
  }
}

const handleEdit = async (row: Dataset) => {
  dialogTitle.value = '编辑数据集'
  datasetForm.id = row.id
  datasetForm.name = row.name
  datasetForm.description = row.description || ''
  dataSource.value = row.data_source as 'upload' | 'select'
  uploadFileList.value = []
  selectedBasicData.value = []
  basicDataList.value = []
  basicDataSearchKeyword.value = ''
  
  dialogVisible.value = true
  
  // 如果是选择模式，加载基础数据并选中已关联的数据
  if (row.data_source === 'select') {
    await loadBasicDataList()
    // 等待DOM更新后再设置选中状态
    if (row.data_ids && row.data_ids.length > 0) {
      await new Promise(resolve => setTimeout(resolve, 100))
      const selectedIds = row.data_ids
      selectedBasicData.value = basicDataList.value.filter(item => 
        selectedIds.includes(item.id)
      )
      // 手动设置表格选中状态
      if (basicDataTableRef.value) {
        basicDataTableRef.value.clearSelection()
        selectedBasicData.value.forEach(item => {
          const row = basicDataList.value.find(d => d.id === item.id)
          if (row) {
            basicDataTableRef.value.toggleRowSelection(row, true)
          }
        })
      }
    }
  }
}

const handleView = (row: Dataset) => {
  ElMessageBox.alert(
    `<div>
      <p><strong>数据集名称：</strong>${row.name}</p>
      <p><strong>描述：</strong>${row.description || '无'}</p>
      <p><strong>数据来源：</strong>${row.data_source === 'upload' ? '上传文件' : '从基础数据选择'}</p>
      <p><strong>数据条数：</strong>${row.data_count}</p>
      <p><strong>创建时间：</strong>${row.created_at}</p>
      <p><strong>更新时间：</strong>${row.updated_at}</p>
    </div>`,
    `查看数据集: ${row.name}`,
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭'
    }
  )
}

const handleDelete = async (row: Dataset) => {
  try {
    await ElMessageBox.confirm(`确定要删除数据集 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteDataset(row.id)
    ElMessage.success('删除成功')
    await loadDatasetList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const handleDataSourceChange = () => {
  uploadFileList.value = []
  selectedBasicData.value = []
  basicDataList.value = []
  basicDataSearchKeyword.value = ''
  // 如果切换到选择模式，加载基础数据列表
  if (dataSource.value === 'select') {
    loadBasicDataList()
  }
}

const handleUploadChange: UploadProps['onChange'] = (file, files) => {
  if (file.raw && !file.raw.name.endsWith('.json')) {
    ElMessage.error('只能上传JSON格式的文件')
    const index = files.findIndex((f) => f.uid === file.uid)
    if (index > -1) {
      files.splice(index, 1)
    }
    return
  }
  uploadFileList.value = files
}

const handleUploadRemove: UploadProps['onRemove'] = (file, files) => {
  if (files) {
    uploadFileList.value = files
  }
}

const handleBasicDataSelectionChange = (selection: BasicDataItem[]) => {
  selectedBasicData.value = selection
}

const handleSelectAll = () => {
  if (basicDataTableRef.value) {
    basicDataTableRef.value.toggleAllSelection()
  }
}

const handleClearSelection = () => {
  if (basicDataTableRef.value) {
    basicDataTableRef.value.clearSelection()
  }
  selectedBasicData.value = []
}

const handleSaveDataset = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    if (dataSource.value === 'upload' && uploadFileList.value.length === 0) {
      ElMessage.warning('请上传JSON文件')
      return
    }

    if (dataSource.value === 'select' && selectedBasicData.value.length === 0) {
      ElMessage.warning('请选择至少一条基础数据')
      return
    }

    if (datasetForm.id) {
      // 编辑
      const updateData: any = {
        name: datasetForm.name,
        description: datasetForm.description
      }
      
      if (dataSource.value === 'select') {
        updateData.data_ids = selectedBasicData.value.map((d) => d.id)
      }
      
      await updateDataset(datasetForm.id, updateData)
      ElMessage.success('更新成功')
    } else {
      // 创建
      if (dataSource.value === 'upload') {
        // 上传文件
        if (uploadFileList.value.length > 0 && uploadFileList.value[0].raw) {
          await uploadDataset(
            uploadFileList.value[0].raw,
            datasetForm.name,
            datasetForm.description
          )
        }
      } else {
        // 从基础数据选择
        await createDataset({
          name: datasetForm.name,
          description: datasetForm.description,
          data_source: 'select',
          data_ids: selectedBasicData.value.map((d) => d.id)
        })
      }
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    await loadDatasetList()
  } catch (error: any) {
    if (error !== false) { // validate 失败返回 false
      ElMessage.error('操作失败: ' + (error.message || '未知错误'))
    }
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  uploadFileList.value = []
  selectedBasicData.value = []
  basicDataList.value = []
  basicDataSearchKeyword.value = ''
}

const formatSize = (size?: number) => {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadDatasetList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadDatasetList()
}
</script>

<style scoped>
.dataset-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.dataset-card {
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

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.dataset-table {
  margin-top: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 40px;
  color: #409eff;
  margin-bottom: 8px;
}

.select-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.select-table {
  margin-top: 12px;
}

.selected-count {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}
</style>

