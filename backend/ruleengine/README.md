# 规则引擎架构设计

## 设计概述

本规则引擎专为电子病历内涵质控系统设计，采用**工作流模式**和**插件化架构**，支持灵活的规则配置和可扩展的原子函数库。

## 核心设计理念

1. **分层架构**：将规则执行、上下文管理、结果评估分离，提高可维护性
2. **配置驱动**：规则通过JSON配置定义，无需修改代码即可调整规则逻辑
3. **插件化函数库**：通过装饰器注册原子函数，易于扩展新的质控能力
4. **上下文管理**：统一的执行上下文，支持节点间数据流转和引用

## 架构组成

### 1. 核心模块 (`core/`)

#### `RuleEngine` (engine.py)
- **职责**：规则执行的主控制器
- **功能**：
  - 解析规则配置
  - 按顺序执行节点
  - 管理执行流程（包括跳过逻辑）
  - 统一错误处理

#### `ExecutionContext` (context.py)
- **职责**：管理执行过程中的数据
- **功能**：
  - 存储病历数据
  - 管理节点输出
  - 解析参数引用（source/output模式）
  - 提取执行证据

#### `ResultEvaluator` (evaluator.py)
- **职责**：评估执行结果
- **功能**：
  - 根据result_rule判断是否通过
  - 渲染解释模板（支持{{node_X.key}}语法）
  - 处理跳过场景

#### `RuleConfig` (config.py)
- **职责**：封装规则配置
- **功能**：
  - 配置解析和验证
  - 提供类型安全的访问接口
  - 提取节点、条件、模板等配置

### 2. 函数注册机制 (`registry.py`)

- **装饰器模式**：通过`@register_function`注册原子函数
- **元数据管理**：记录函数描述、输入输出、分类、标签
- **动态发现**：支持前端动态获取可用函数列表

### 3. 原子函数库 (`functions/`)

按功能分类组织：
- `text_extract.py`：文本提取函数
- `text_analyze.py`：文本分析函数（成分缺失、描述不清等）
- `logic_check.py`：逻辑校验函数
- `numeric_check.py`：数值检查函数
- `llm_based.py`：基于LLM的判断函数

## 规则配置格式

```json
{
  "rule_id": "rule_001",
  "rule_name": "主诉完整性检查",
  "module": "入院记录",
  "description": "检查主诉是否包含必要成分",
  "type": "成分缺失",
  "fields_name": [["入院记录", "主诉"]],
  "function_list": {
    "nodes": [
      {
        "id": 1,
        "function": "extract_field_content",
        "params": {
          "field_name": ["入院记录", "主诉"],
          "medical_record": {"source": "context", "key": "medical_record"}
        },
        "outputs": {
          "text": "result"
        }
      },
      {
        "id": 2,
        "function": "component_missing",
        "params": {
          "text": {"source": 1, "output": "text"},
          "components": "时间、症状",
          "logic_definition": ""
        },
        "outputs": {
          "is_missing": "result"
        }
      }
    ],
    "result_rule": {
      "pass": {
        "source": 2,
        "output": "is_missing",
        "expect": false
      },
      "skipped_1": {
        "source": 1,
        "output": "is_empty",
        "expect": true
      }
    },
    "explanation_template": {
      "pass": "主诉包含必要成分：{{node_2.evidence}}",
      "fail": "主诉缺失必要成分：{{node_2.evidence}}",
      "skipped_1": "主诉为空，无需检查"
    }
  },
  "deduct": 10
}
```

## 执行流程

1. **初始化**：创建RuleEngine，解析配置，初始化ExecutionContext
2. **执行节点**：按id顺序执行每个节点
   - 解析参数（处理引用）
   - 调用注册的函数
   - 保存节点输出
   - 检查跳过条件
3. **评估结果**：根据result_rule判断是否通过
4. **生成解释**：渲染explanation_template
5. **提取证据**：收集关键节点输出
6. **返回结果**：构建标准化的质控结果

## 扩展性设计

### 添加新函数

1. 在`functions/`目录下创建函数文件
2. 使用`@register_function`装饰器注册
3. 函数返回标准格式：`{"result": ..., "evidence": ..., "details": ...}`

### 支持新功能

- **并行执行**：可在RuleEngine中扩展并行节点执行
- **条件分支**：可在配置中增加条件判断节点
- **循环处理**：可添加循环节点类型

## 优势

1. **清晰的职责分离**：每个模块职责单一，易于理解和维护
2. **高度可配置**：规则逻辑完全由配置驱动
3. **易于扩展**：插件化函数库，新增功能无需修改核心代码
4. **类型安全**：通过RuleConfig提供类型安全的配置访问
5. **错误处理完善**：统一的异常处理和错误返回格式

## 与现有系统的集成

- 与FastAPI路由层集成：`services/execution_service.py`调用RuleEngine
- 与数据库模型集成：规则配置存储在`qc_rule`表的`config`字段
- 与前端集成：通过API暴露规则执行能力

