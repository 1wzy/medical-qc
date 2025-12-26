<template>
  <div class="rule-manage-container">
    <el-card class="rule-card">
      <template #header>
        <div class="card-header">
          <span class="title">质控规则管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新增规则
          </el-button>
        </div>
      </template>

      <el-table
        :data="rules"
        v-loading="loading"
        stripe
        class="rule-table"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" min-width="200" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" effect="light">
              {{ row.type || 'unknown' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deduct" label="扣分" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'draft'"
              size="small"
              type="success"
              @click="handlePublish(row)"
            >
              发布
            </el-button>
            <el-button
              v-if="row.status === 'published'"
              size="small"
              type="warning"
              @click="handleOffline(row)"
            >
              下线
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑规则对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入规则名称" />
        </el-form-item>

        <el-form-item label="所属模块" prop="module">
          <el-input v-model="form.module" placeholder="如：入院记录、出院记录等" />
        </el-form-item>

        <el-form-item label="规则类型" prop="type">
          <el-select v-model="form.type" style="width: 100%" placeholder="请选择规则类型">
            <el-option label="字段完整性" value="字段完整性" />
            <el-option label="字段一致性" value="字段一致性" />
            <el-option label="逻辑性" value="逻辑性" />
            <el-option label="格式规范性" value="格式规范性" />
            <el-option label="其他" value="unknown" />
          </el-select>
        </el-form-item>

        <el-form-item label="扣分" prop="deduct">
          <el-input-number
            v-model="form.deduct"
            :min="0"
            :max="100"
            placeholder="扣分"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规则描述"
          />
        </el-form-item>

        <el-form-item label="规则配置" prop="config">
          <el-alert
            type="info"
            :closable="false"
            style="margin-bottom: 10px"
          >
            <template #title>
              <div>
                <div>规则配置JSON（必需）</div>
                <div style="font-size: 12px; margin-top: 5px">
                  建议先在"API测试"页面使用"规则开发工具"测试规则配置，测试通过后再创建规则
                </div>
              </div>
            </template>
          </el-alert>
          <el-input
            v-model="configJson"
            type="textarea"
            :rows="12"
            placeholder='请输入规则配置JSON，例如：{"rule_id": "test_001", "rule_name": "测试规则", "function_list": {...}}'
            @blur="validateConfigJson"
          />
          <div v-if="configError" class="error-text">{{ configError }}</div>
        </el-form-item>

        <el-form-item label="字段列表" prop="fields_name">
          <el-alert
            type="info"
            :closable="false"
            style="margin-bottom: 10px"
          >
            <template #title>
              字段列表（可选），格式：["section", "field"]，例如：["入院记录", "主诉"]
            </template>
          </el-alert>
          <div v-for="(field, index) in form.fields_name" :key="index" class="field-item">
            <el-input
              v-model="field[0]"
              placeholder="章节"
              style="width: 200px; margin-right: 10px"
            />
            <el-input
              v-model="field[1]"
              placeholder="字段"
              style="width: 200px; margin-right: 10px"
            />
            <el-button
              type="danger"
              :icon="Delete"
              circle
              @click="removeField(index)"
            />
          </div>
          <el-button
            type="primary"
            :icon="Plus"
            plain
            @click="addField"
            style="margin-top: 10px"
          >
            添加字段
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.auto_publish">
            创建后立即发布（不勾选则保存为草稿）
          </el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getRules, createRule, updateRule, publishRule, type Rule, type RuleCreate, type RuleUpdate } from '@/api/rule'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const configError = ref('')

const rules = ref<Rule[]>([])
const currentRuleId = ref<number | null>(null)

const form = reactive<RuleCreate & { fields_name: string[][] }>({
  name: '',
  module: '',
  description: '',
  type: 'unknown',
  deduct: 0,
  fields_name: [],
  config: {},
  auto_publish: false
})

const configJson = ref('')

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  config: [
    { required: true, message: '请输入规则配置', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() =>
  isEditing.value ? '编辑规则' : '新增规则'
)

// 验证配置JSON
const validateConfigJson = () => {
  configError.value = ''
  if (!configJson.value.trim()) {
    return
  }
  try {
    const parsed = JSON.parse(configJson.value)
    form.config = parsed
  } catch (e) {
    const message = e instanceof Error ? e.message : '未知错误'
    configError.value = `JSON格式错误: ${message}`
  }
}

// 加载规则列表
const loadRules = async () => {
  loading.value = true
  try {
    const data = await getRules()
    // 按ID从小到大排序
    rules.value = data.sort((a, b) => a.id - b.id)
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('加载规则列表失败: ' + message)
  } finally {
    loading.value = false
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  isEditing.value = false
  currentRuleId.value = null
  form.name = ''
  form.module = ''
  form.description = ''
  form.type = 'unknown'
  form.deduct = 0
  form.fields_name = []
  form.config = {}
  form.auto_publish = false
  configJson.value = ''
  configError.value = ''
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row: Rule) => {
  isEditing.value = true
  currentRuleId.value = row.id
  form.name = row.name
  form.module = row.module || ''
  form.description = row.description || ''
  form.type = row.type
  form.deduct = row.deduct
  form.fields_name = row.fields_name || []
  form.config = row.config
  form.auto_publish = false
  configJson.value = JSON.stringify(row.config, null, 2)
  configError.value = ''
  dialogVisible.value = true
}

// 添加字段
const addField = () => {
  form.fields_name.push(['', ''])
}

// 删除字段
const removeField = (index: number) => {
  form.fields_name.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  // 验证配置JSON
  validateConfigJson()
  if (configError.value) {
    ElMessage.error('请修正规则配置JSON格式')
    return
  }

  if (!form.config || Object.keys(form.config).length === 0) {
    ElMessage.error('请输入规则配置')
    return
  }

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditing.value && currentRuleId.value) {
        // 更新规则
        const updateData: RuleUpdate = {
          name: form.name,
          module: form.module,
          description: form.description,
          type: form.type,
          deduct: form.deduct,
          fields_name: form.fields_name,
          config: form.config
        }
        await updateRule(currentRuleId.value, updateData)
        ElMessage.success('规则更新成功')
      } else {
        // 创建规则
        const createData: RuleCreate = {
          name: form.name,
          module: form.module,
          description: form.description,
          type: form.type,
          deduct: form.deduct,
          fields_name: form.fields_name,
          config: form.config,
          auto_publish: form.auto_publish
        }
        await createRule(createData)
        ElMessage.success(form.auto_publish ? '规则创建并发布成功' : '规则创建成功')
      }
      dialogVisible.value = false
      await loadRules()
    } catch (error) {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('操作失败: ' + message)
    } finally {
      submitting.value = false
    }
  })
}

// 发布规则
const handlePublish = async (row: Rule) => {
  try {
    await ElMessageBox.confirm('确定要发布该规则吗？发布后规则可以被执行。', '确认发布', {
      type: 'warning'
    })
    await publishRule(row.id)
    ElMessage.success('规则发布成功')
    await loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('发布失败: ' + message)
    }
  }
}

// 下线规则（暂时用更新状态实现）
const handleOffline = async (row: Rule) => {
  try {
    await ElMessageBox.confirm('确定要下线该规则吗？下线后规则将无法被执行。', '确认下线', {
      type: 'warning'
    })
    const updateData: RuleUpdate = {
      status: 'offline'
    }
    await updateRule(row.id, updateData)
    ElMessage.success('规则已下线')
    await loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('下线失败: ' + message)
    }
  }
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
    published: 'success',
    draft: 'info',
    offline: 'warning'
  }
  return map[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    published: '已发布',
    draft: '草稿',
    offline: '已下线'
  }
  return map[status] || status
}

// 获取类型标签类型
const getTypeTagType = (type: string) => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    '字段完整性': 'success',
    '字段一致性': 'warning',
    '逻辑性': 'danger',
    '格式规范性': 'info'
  }
  return map[type] || 'info'
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.rule-manage-container {
  padding: 0;
}

.rule-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 600;
  font-size: 16px;
}

.field-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 5px;
}
</style>
