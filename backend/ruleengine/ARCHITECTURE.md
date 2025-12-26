# 规则引擎架构设计文档

## 一、设计目标

为电子病历内涵质控系统设计一个**可扩展、易维护、配置驱动**的规则执行引擎，支持：
- 灵活的规则配置（无需修改代码）
- 插件化的原子函数库
- 清晰的执行流程和错误处理
- 适合毕设展示的架构设计

## 二、整体架构

```
ruleengine/
├── core/                    # 核心执行引擎
│   ├── engine.py           # RuleEngine - 主执行器
│   ├── context.py          # ExecutionContext - 上下文管理
│   ├── evaluator.py        # ResultEvaluator - 结果评估
│   └── config.py           # RuleConfig - 配置模型
├── functions/              # 原子函数库（按功能分类）
│   ├── text_extract.py    # 文本提取
│   ├── text_analyze.py    # 文本分析
│   ├── logic_check.py     # 逻辑校验
│   ├── numeric_check.py   # 数值检查
│   └── llm_based.py       # LLM类函数
├── registry.py            # 函数注册机制
├── model_request.py       # LLM调用封装
└── regex_tools.py         # 正则工具函数
```

## 三、核心模块设计

### 3.1 RuleEngine (核心执行器)

**职责**：
- 解析规则配置
- 协调执行流程
- 统一错误处理

**设计要点**：
- 单一职责：只负责执行流程控制
- 依赖注入：通过构造函数接收配置
- 异常安全：所有异常都转换为标准错误结果

### 3.2 ExecutionContext (执行上下文)

**职责**：
- 管理执行过程中的所有数据
- 解析参数引用
- 提取执行证据

**设计要点**：
- 集中管理：所有执行数据都在上下文中
- 引用解析：支持 `{"source": "node1", "output": "x"}` 语法
- 多引用拼接：支持列表形式的多个引用

### 3.3 ResultEvaluator (结果评估器)

**职责**：
- 根据配置判断是否通过
- 渲染解释模板
- 处理跳过场景

**设计要点**：
- 模板语法：支持 `{{node_X.key}}` 占位符
- 状态处理：区分 pass/fail/skipped 三种状态
- 可扩展：易于添加新的评估逻辑

### 3.4 RuleConfig (配置模型)

**职责**：
- 封装规则配置
- 提供类型安全的访问接口
- 配置验证

**设计要点**：
- 封装性：隐藏配置的内部结构
- 类型安全：通过属性访问，避免键错误
- 验证机制：初始化时验证必需字段

## 四、函数注册机制

### 4.1 装饰器模式

```python
@register_function(
    name="extract_field",
    description="提取字段",
    category="文本提取",
    inputs=[...],
    outputs={...},
    tags=["text", "extract"]
)
def extract_field(...):
    ...
```

### 4.2 元数据管理

每个注册的函数都包含：
- 函数对象
- 描述信息
- 输入输出说明
- 分类和标签

便于前端动态生成函数选择器。

## 五、执行流程

```
1. 初始化
   ├── 创建 RuleEngine
   ├── 解析 RuleConfig
   └── 初始化 ExecutionContext

2. 执行节点循环
   ├── 解析节点参数（处理引用）
   ├── 调用注册的函数
   ├── 保存节点输出
   └── 检查跳过条件

3. 评估结果
   ├── 检查是否跳过
   ├── 根据 result_rule 判断
   └── 生成解释文本

4. 返回结果
   └── 构建标准化结果字典
```

## 六、规则配置格式

### 6.1 基本结构

```json
{
  "rule_id": "唯一标识",
  "rule_name": "规则名称",
  "module": "所属模块",
  "description": "规则描述",
  "type": "规则类型",
  "fields_name": [["section", "field"]],
  "function_list": {
    "nodes": [...],
    "result_rule": {...},
    "explanation_template": {...}
  },
  "deduct": 10
}
```

### 6.2 节点配置

```json
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
}
```

### 6.3 参数引用

- **单引用**：`{"source": "node1", "output": "text"}`
- **多引用拼接**：`[{"source": "n1", "output": "x"}, {"source": "n2", "output": "y"}]`
- **嵌套引用**：支持在复杂结构中引用

## 七、扩展性设计

### 7.1 添加新函数

1. 在 `functions/` 对应分类文件中添加函数
2. 使用 `@register_function` 装饰器
3. 返回标准格式：`{"result": ..., "evidence": ..., "details": ...}`

### 7.2 支持新功能

- **并行执行**：扩展 `RuleEngine._execute_nodes()` 支持并行
- **条件分支**：在配置中增加条件判断节点类型
- **循环处理**：添加循环节点类型

## 八、与系统集成

### 8.1 后端集成

- `services/execution_service.py` 调用 `RuleEngine`
- 规则配置存储在 `qc_rule` 表
- 执行结果存储在 `qc_rule_execution_record` 表

### 8.2 API 接口

- `POST /api/rules` - 创建规则
- `POST /api/qc/execute` - 执行规则
- `GET /api/rules` - 获取规则列表

## 九、设计优势

1. **分层清晰**：核心逻辑与业务函数分离
2. **配置驱动**：规则逻辑完全由配置控制
3. **易于扩展**：插件化函数库，新增功能简单
4. **类型安全**：通过配置模型提供类型安全访问
5. **错误处理完善**：统一的异常处理机制
6. **适合毕设**：体现软件工程的设计思路和最佳实践

## 十、后续优化方向

1. **性能优化**：支持节点并行执行
2. **缓存机制**：LLM调用结果缓存
3. **规则版本管理**：支持规则版本回滚
4. **执行监控**：详细的执行日志和性能统计
5. **规则验证**：配置保存前的语法和逻辑验证

