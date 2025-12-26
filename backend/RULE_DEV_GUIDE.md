# 规则开发指南

## 🎯 问题

前端执行质控需要提前存好规则，但规则配置JSON很复杂，需要一个地方：
1. **编写规则**
2. **测试规则**（确保规则可用）
3. **导入规则**（测试通过后）

## 💡 解决方案

提供了两种方式：

### 方式1：API接口（推荐）

通过 Swagger UI 或前端调用规则开发接口。

#### 1. 测试规则（不保存）

**接口**：`POST /api/rule-dev/test`

```json
{
  "rule_config": {
    "rule_id": "test_001",
    "rule_name": "测试规则",
    "module": "test",
    "description": "测试",
    "type": "test",
    "fields_name": [],
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
        "pass": "字段存在",
        "fail": "字段为空"
      }
    },
    "deduct": 0
  },
  "medical_record": {
    "入院记录": {
      "主诉": "患者因头痛3天入院"
    }
  }
}
```

**返回**：
```json
{
  "success": true,
  "passed": true,
  "flag": 1,
  "explanation": "字段存在",
  "answer": {...},
  "duration_ms": 5
}
```

#### 2. 导入规则（测试通过后）

**接口**：`POST /api/rule-dev/import`

```json
{
  "name": "主诉完整性检查",
  "module": "入院记录",
  "description": "检查主诉字段是否存在",
  "type": "字段完整性",
  "deduct": 10,
  "fields_name": [["入院记录", "主诉"]],
  "rule_config": {
    // 完整的规则配置（同上）
  }
}
```

**返回**：创建的规则信息（包含数据库ID）

**注意**：导入后规则状态为 `draft`（草稿），需要发布后才能使用。

#### 3. 发布规则（导入后必须执行）

**接口**：`POST /api/rules/{id}/publish`

将规则状态从 `draft` 改为 `published`，只有已发布的规则才能被前端执行质控时使用。

### 方式2：命令行工具

使用 `rule_dev_tool.py` 脚本。

#### 1. 列出可用函数

```bash
python rule_dev_tool.py list
```

#### 2. 创建规则模板

```bash
python rule_dev_tool.py template rule_template.json
```

#### 3. 测试规则

```bash
# 使用默认测试病历
python rule_dev_tool.py test rule.json

# 使用自定义测试病历
python rule_dev_tool.py test rule.json medical.json
```

#### 4. 生成导入JSON

```bash
# 输出到控制台
python rule_dev_tool.py import rule.json

# 保存到文件
python rule_dev_tool.py import rule.json import_data.json
```

## 📝 工作流程

### 完整流程

```
1. 编写规则配置JSON
   ↓
2. 测试规则（POST /api/rule-dev/test）
   ↓
3. 如果测试失败，修改规则配置
   ↓
4. 重复步骤2-3直到测试通过
   ↓
5. 导入规则（POST /api/rule-dev/import）
   ✅ 规则已保存到数据库，但状态为 draft（草稿）
   ↓
6. 发布规则（POST /api/rules/{id}/publish）
   ✅ 状态变为 published，前端才能使用该规则执行质控
```

**重要说明**：
- **导入后**：规则已经在数据库中，可以通过 `GET /api/rules/` 查看
- **但只有发布后**：规则状态变为 `published`，才能被前端执行质控时使用
- 执行规则时会检查 `status == "published"`，只有已发布的规则才能执行

### 使用命令行工具

```
1. 创建模板
   python rule_dev_tool.py template my_rule.json
   
2. 编辑规则配置
   # 用编辑器打开 my_rule.json，修改配置
   
3. 测试规则
   python rule_dev_tool.py test my_rule.json test_medical.json
   
4. 如果测试通过，生成导入JSON
   python rule_dev_tool.py import my_rule.json import.json
   
5. 在 Swagger UI 中使用 import.json 创建规则
```

## 🎨 规则模板示例

```json
{
  "rule_id": "主诉完整性检查_001",
  "rule_name": "主诉完整性检查",
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
      },
      {
        "id": 2,
        "function": "count_characters",
        "params": {
          "text": {"source": 1, "output": "text"},
          "count_chinese_only": true
        },
        "outputs": {
          "count": "result"
        }
      }
    ],
    "result_rule": {
      "pass": {
        "source": 2,
        "output": "count",
        "expect": 10  // 至少10个字符
      }
    },
    "explanation_template": {
      "pass": "主诉字段存在且长度符合要求（{{node_2.count}}个字符）",
      "fail": "主诉字段长度不足（{{node_2.count}}个字符，要求至少10个字符）"
    }
  },
  "deduct": 10
}
```

## ✅ 优势

1. **分离开发和生产**：规则先在开发环境测试，通过后再导入
2. **快速迭代**：可以快速测试规则，无需每次都创建到数据库
3. **批量导入**：可以准备多个规则，批量测试后导入
4. **版本控制**：规则配置JSON可以纳入版本控制

## 🔧 下一步

1. 使用 `rule_dev_tool.py template` 创建规则模板
2. 编辑规则配置
3. 使用 `rule_dev_tool.py test` 测试规则
4. 测试通过后，使用 `POST /api/rule-dev/import` 导入
5. 在 Swagger UI 中创建规则并发布

