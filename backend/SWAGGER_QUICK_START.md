# Swagger UI 快速测试指南

## 📋 测试流程概览

```
1. 创建规则 (POST /api/rules/)
   ↓
2. 发布规则 (POST /api/rules/{rule_id}/publish)
   ↓
3. 执行规则 (POST /api/qc/execute)
   ↓
4. 查看结果
```

---

## 🚀 详细步骤

### 步骤 1：创建规则

**接口**：`POST /api/rules/`

1. 在 Swagger UI 中找到 `POST /api/rules/`（在 `rules` 标签下）
2. 点击 **"Try it out"** 按钮
3. 在 **Request body** 文本框中，粘贴以下 JSON：

```json
{
  "name": "测试规则-主诉字段检查",
  "module": "入院记录",
  "description": "检查主诉字段是否存在且不为空",
  "type": "字段完整性",
  "deduct": 10,
  "fields_name": [
    ["入院记录", "主诉"]
  ],
  "config": {
    "rule_id": "test_swagger_001",
    "rule_name": "测试规则-主诉字段检查",
    "module": "入院记录",
    "description": "检查主诉字段是否存在且不为空",
    "type": "字段完整性",
    "fields_name": [
      ["入院记录", "主诉"]
    ],
    "function_list": {
      "nodes": [
        {
          "id": 1,
          "function": "extract_field_content",
          "params": {
            "field_name": ["入院记录", "主诉"]
          },
          "outputs": {
            "text": "result",
            "is_empty": "is_empty"
          }
        }
      ],
      "result_rule": {
        "pass": {
          "source": 1,
          "output": "is_empty",
          "expect": false
        }
      },
      "explanation_template": {
        "pass": "主诉字段存在且不为空",
        "fail": "主诉字段为空或不存在"
      }
    },
    "deduct": 10
  }
}
```

4. 点击 **"Execute"** 按钮
5. **重要**：记录返回结果中的 `id` 字段（例如：`"id": 1`），后续步骤需要使用

**预期返回**：
```json
{
  "id": 1,
  "name": "测试规则-主诉字段检查",
  "status": "draft",
  "version": 1,
  ...
}
```

---

### 步骤 2：发布规则

**接口**：`POST /api/rules/{rule_id}/publish`

1. 找到 `POST /api/rules/{rule_id}/publish` 接口
2. 点击 **"Try it out"** 按钮
3. 在 `rule_id` 参数输入框中，输入步骤1返回的 `id`（例如：`1`）
4. 点击 **"Execute"** 按钮
5. 确认返回结果中的 `status` 为 `"published"`

**预期返回**：
```json
{
  "id": 1,
  "name": "测试规则-主诉字段检查",
  "status": "published",  // 注意：状态变为 published
  "version": 1,
  ...
}
```

---

### 步骤 3：执行规则

**接口**：`POST /api/qc/execute`

1. 找到 `POST /api/qc/execute` 接口（在 `execute` 标签下）
2. 点击 **"Try it out"** 按钮
3. 在 **Request body** 文本框中，粘贴以下 JSON（**将 `rule_id` 替换为步骤1返回的ID**）：

```json
{
  "rule_id": 1,
  "medical_record": {
    "入院记录": {
      "主诉": "患者因头痛3天入院",
      "现病史": "患者3天前无明显诱因出现头痛，呈持续性胀痛",
      "既往史": "无特殊"
    }
  },
  "medical_id": "test_medical_001"
}
```

4. 点击 **"Execute"** 按钮
5. 查看返回结果

**预期返回（字段存在）**：
```json
{
  "rule_id": 1,
  "rule_name": "测试规则-主诉字段检查",
  "description": "检查主诉字段是否存在且不为空",
  "module": "入院记录",
  "passed": true,
  "flag": 1,
  "deduct": 0,
  "answer": {
    "node_1.text": "入院记录.主诉>>>患者因头痛3天入院\n",
    "node_1.is_empty": false
  },
  "explanation": "主诉字段存在且不为空",
  "type": "字段完整性",
  "fields_name": [
    ["入院记录", "主诉"]
  ]
}
```

---

### 步骤 4：测试不通过场景

使用相同的规则，但使用空字段的病历：

```json
{
  "rule_id": 1,
  "medical_record": {
    "入院记录": {
      "主诉": "",
      "现病史": "患者..."
    }
  },
  "medical_id": "test_medical_002"
}
```

**预期返回（字段为空）**：
```json
{
  "rule_id": 1,
  "rule_name": "测试规则-主诉字段检查",
  "passed": false,
  "flag": 0,
  "deduct": 10,
  "explanation": "主诉字段为空或不存在",
  ...
}
```

---

## 📊 结果字段说明

| 字段 | 说明 | 可能值 |
|------|------|--------|
| `passed` | 是否通过 | `true` / `false` |
| `flag` | 状态标志 | `1`=通过, `0`=不通过, `-1`=错误 |
| `deduct` | 扣分 | 不通过时显示扣分数 |
| `explanation` | 解释说明 | 质控结果的文字说明 |
| `answer` | 执行证据 | 包含各节点的输出结果 |

---

## 🔍 其他有用的接口

### 查看所有规则
- **接口**：`GET /api/rules/`
- **用途**：查看所有已创建的规则列表

### 查看单个规则详情
- **接口**：`GET /api/rules/{rule_id}`
- **用途**：查看指定规则的完整配置

### 更新规则
- **接口**：`PUT /api/rules/{rule_id}`
- **用途**：修改规则配置（需要先取消发布）

---

## ⚠️ 常见问题

### Q1: 执行时返回 404 "Rule not found"
**原因**：规则未发布或 rule_id 错误
**解决**：确保已执行步骤2（发布规则），并检查 rule_id 是否正确

### Q2: 执行时返回 flag: -1（错误）
**原因**：规则配置有误或函数未注册
**解决**：
- 检查规则配置中的 `function` 名称是否正确（当前只有 `extract_field_content`）
- 检查节点配置格式是否正确

### Q3: 创建规则时返回验证错误
**原因**：JSON 格式错误或缺少必需字段
**解决**：检查 JSON 格式，确保所有必需字段都存在

---

## 💡 提示

1. **规则ID**：创建规则后，务必记录返回的 `id`，后续步骤都需要使用
2. **规则状态**：只有 `status = "published"` 的规则才能被执行
3. **函数名称**：当前只有 `extract_field_content` 函数可用，其他函数需要迁移后才能使用

---

## 🎯 快速复制模板

### 创建规则模板
```json
{
  "name": "规则名称",
  "module": "模块名",
  "description": "规则描述",
  "type": "规则类型",
  "deduct": 10,
  "fields_name": [["section", "field"]],
  "config": {
    "rule_id": "唯一标识",
    "rule_name": "规则名称",
    "module": "模块名",
    "description": "规则描述",
    "type": "规则类型",
    "fields_name": [["section", "field"]],
    "function_list": {
      "nodes": [{
        "id": 1,
        "function": "extract_field_content",
        "params": {
          "field_name": ["section", "field"]
        },
        "outputs": {
          "text": "result",
          "is_empty": "is_empty"
        }
      }],
      "result_rule": {
        "pass": {
          "source": 1,
          "output": "is_empty",
          "expect": false
        }
      },
      "explanation_template": {
        "pass": "通过说明",
        "fail": "不通过说明"
      }
    },
    "deduct": 10
  }
}
```

### 执行规则模板
```json
{
  "rule_id": 1,
  "medical_record": {
    "section": {
      "field": "值"
    }
  },
  "medical_id": "optional_id"
}
```

