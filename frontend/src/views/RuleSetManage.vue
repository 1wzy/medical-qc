<template>
  <div class="rule-set-manage-container">
    <el-card class="rule-set-card">
      <template #header>
        <div class="card-header">
          <span class="title">规则集管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建规则集
          </el-button>
        </div>
      </template>

      <el-table
        :data="ruleSets"
        v-loading="loading"
        stripe
        class="rule-set-table"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则集名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="rule_count" label="规则数量" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.rule_count || 0 }} 条</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" effect="light">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" type="primary" @click="openManageDialog(row)">管理规则</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑规则集对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="规则集名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入规则集名称" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规则集描述"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理规则对话框 -->
    <el-dialog
      v-model="manageDialogVisible"
      title="管理规则集中的规则"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentRuleSet">
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        >
          <template #title>
            规则集：{{ currentRuleSet.name }}
          </template>
        </el-alert>

        <el-transfer
          v-model="selectedRules"
          :data="availableRules"
          :titles="['可用规则', '已选规则']"
          :props="{ key: 'id', label: 'name' }"
          filterable
          filter-placeholder="搜索规则"
        />
      </div>

      <template #footer>
        <el-button @click="manageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRules" :loading="savingRules">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRules, type Rule } from '@/api/rule'

interface RuleSet {
  id: number
  name: string
  description?: string
  rule_count?: number
  status: 'active' | 'inactive'
  rules?: number[]
}

const loading = ref(false)
const submitting = ref(false)
const savingRules = ref(false)
const dialogVisible = ref(false)
const manageDialogVisible = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const currentRuleSet = ref<RuleSet | null>(null)
const selectedRules = ref<number[]>([])
const availableRules = ref<Rule[]>([])

const ruleSets = ref<RuleSet[]>([
  // 模拟数据，后续对接后端API
  { id: 1, name: '入院记录质控规则集', description: '用于入院记录的质控规则', rule_count: 5, status: 'active' },
  { id: 2, name: '出院记录质控规则集', description: '用于出院记录的质控规则', rule_count: 3, status: 'active' }
])

const form = reactive<RuleSet>({
  id: 0,
  name: '',
  description: '',
  status: 'active',
  rule_count: 0
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入规则集名称', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() =>
  isEditing.value ? '编辑规则集' : '新建规则集'
)

// 加载规则列表（用于规则集管理）
const loadAvailableRules = async () => {
  try {
    availableRules.value = await getRules()
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('加载规则列表失败: ' + message)
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  isEditing.value = false
  form.id = 0
  form.name = ''
  form.description = ''
  form.status = 'active'
  form.rule_count = 0
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row: RuleSet) => {
  isEditing.value = true
  form.id = row.id
  form.name = row.name
  form.description = row.description || ''
  form.status = row.status
  form.rule_count = row.rule_count || 0
  dialogVisible.value = true
}

// 打开管理规则对话框
const openManageDialog = async (row: RuleSet) => {
  currentRuleSet.value = row
  selectedRules.value = row.rules || []
  await loadAvailableRules()
  manageDialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      // TODO: 对接后端API
      if (isEditing.value) {
        // 更新规则集
        const index = ruleSets.value.findIndex(r => r.id === form.id)
        if (index !== -1) {
          ruleSets.value[index] = { ...form }
        }
        ElMessage.success('规则集更新成功')
      } else {
        // 创建规则集
        const newRuleSet: RuleSet = {
          ...form,
          id: ruleSets.value.length + 1
        }
        ruleSets.value.push(newRuleSet)
        ElMessage.success('规则集创建成功')
      }
      dialogVisible.value = false
    } catch (error) {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('操作失败: ' + message)
    } finally {
      submitting.value = false
    }
  })
}

// 保存规则集中的规则
const handleSaveRules = async () => {
  if (!currentRuleSet.value) return
  
  savingRules.value = true
  try {
    // TODO: 对接后端API保存规则集和规则的关联
    const ruleSetId = currentRuleSet.value.id
    const index = ruleSets.value.findIndex(r => r.id === ruleSetId)
    if (index !== -1 && ruleSets.value[index]) {
      const ruleSet = ruleSets.value[index]
      ruleSet.rules = [...selectedRules.value]
      ruleSet.rule_count = selectedRules.value.length
    }
    ElMessage.success('规则保存成功')
    manageDialogVisible.value = false
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('保存失败: ' + message)
  } finally {
    savingRules.value = false
  }
}

// 删除规则集
const handleDelete = async (row: RuleSet) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则集吗？', '确认删除', {
      type: 'warning'
    })
    // TODO: 对接后端API
    const index = ruleSets.value.findIndex(r => r.id === row.id)
    if (index !== -1) {
      ruleSets.value.splice(index, 1)
    }
    ElMessage.success('规则集删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('删除失败: ' + message)
    }
  }
}

onMounted(() => {
  // 可以在这里加载规则集列表
})
</script>

<style scoped>
.rule-set-manage-container {
  padding: 0;
}

.rule-set-card {
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
</style>

