# 前端后端连接测试指南

## 📋 准备工作

### 1. 安装依赖

前端需要安装 `axios` 用于发送 HTTP 请求：

```bash
cd frontend
npm install axios
```

### 2. 启动后端

确保后端服务正在运行：

```bash
cd backend
python main.py
```

或者使用 uvicorn：

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端应该运行在 `http://127.0.0.1:8000`

### 3. 启动前端

```bash
cd frontend
npm run dev
```

前端通常运行在 `http://localhost:5173`（Vite 默认端口）

## 🧪 测试步骤

### 方法1：使用测试页面（推荐）

1. 打开浏览器访问前端地址（如 `http://localhost:5173`）
2. 登录系统（任意用户名密码即可）
3. 在侧边栏找到"API测试"菜单项，点击进入
4. 点击"测试健康检查接口"按钮
5. 如果看到绿色成功提示，说明连接正常
6. 点击"测试获取规则列表"按钮，测试 API 接口

### 方法2：直接访问测试页面

如果不想登录，可以直接访问：
```
http://localhost:5173/api-test
```

### 方法3：使用浏览器控制台

打开浏览器开发者工具（F12），在控制台输入：

```javascript
// 测试健康检查
fetch('http://127.0.0.1:8000/health')
  .then(res => res.json())
  .then(data => console.log('健康检查:', data))
  .catch(err => console.error('连接失败:', err))

// 测试获取规则列表
fetch('http://127.0.0.1:8000/api/rules/')
  .then(res => res.json())
  .then(data => console.log('规则列表:', data))
  .catch(err => console.error('获取失败:', err))
```

## ✅ 预期结果

### 健康检查成功
```json
{
  "status": "ok"
}
```

### 获取规则列表成功
```json
[
  {
    "id": 1,
    "name": "规则名称",
    "status": "published",
    ...
  }
]
```

## ❌ 常见问题

### 1. CORS 错误

**错误信息**：`Access to fetch at 'http://127.0.0.1:8000/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**解决方法**：
- 检查后端 `config.py` 中的 `ENABLE_CORS` 是否为 `true`
- 检查后端 `main.py` 中 CORS 中间件是否正确配置
- 重启后端服务

### 2. 连接被拒绝

**错误信息**：`Failed to fetch` 或 `ERR_CONNECTION_REFUSED`

**解决方法**：
- 确认后端服务正在运行
- 检查后端端口是否为 8000
- 检查防火墙设置

### 3. 404 Not Found

**错误信息**：`404 Not Found`

**解决方法**：
- 检查 API 路径是否正确（应该是 `/api/rules/` 而不是 `/rules/`）
- 检查后端路由配置

### 4. 前端找不到 axios

**错误信息**：`Cannot find module 'axios'`

**解决方法**：
```bash
cd frontend
npm install axios
```

## 📝 API 配置

API 配置在 `frontend/src/api/config.ts`：

```typescript
export const API_BASE_URL = 'http://127.0.0.1:8000/api'
```

如果需要修改后端地址，可以：
1. 修改 `config.ts` 文件
2. 或者创建 `.env` 文件设置 `VITE_API_BASE_URL`

## 🔍 调试技巧

1. **查看网络请求**：打开浏览器开发者工具 → Network 标签，查看请求和响应
2. **查看控制台**：查看 Console 标签中的错误信息
3. **后端日志**：查看后端终端输出的日志信息

## 📚 相关文件

- `frontend/src/api/config.ts` - API 配置
- `frontend/src/api/request.ts` - 请求封装
- `frontend/src/api/test.ts` - 测试接口
- `frontend/src/views/ApiTest.vue` - 测试页面
- `backend/main.py` - 后端主文件
- `backend/config.py` - 后端配置

