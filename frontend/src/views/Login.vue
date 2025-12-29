<template>
  <div class="login-container">
    <div class="login-left">
      <!-- logo -->
      <div class="logo-section">
        <div class="logo-img">
          <el-icon :size="40"><Monitor /></el-icon>
        </div>
        <h1 class="logo-title">医疗质控系统</h1>
      </div>

      <!-- 登录表单 -->
      <div class="login-form-wrapper">
        <div class="form-header">
          <h2 class="welcome-title">欢迎回来</h2>
          <p class="welcome-subtitle">请输入您的账号信息登录系统</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember" @change="handleRememberChange">
              记住我
            </el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>

          <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">
            登录
          </el-button>

          <el-divider>
            <span class="divider-text">快速登录</span>
          </el-divider>

          <div class="quick-login">
            <el-button class="quick-btn" @click="quickLogin('admin')">
              <el-icon><User /></el-icon>
              <span>管理员</span>
            </el-button>
            <el-button class="quick-btn" @click="quickLogin('user')">
              <el-icon><UserFilled /></el-icon>
              <span>普通用户</span>
            </el-button>
          </div>
        </el-form>
      </div>
    </div>

    <div class="login-right">
      <div class="brand-background"></div>
      <div class="brand-content">
        <el-carousel
          :interval="5000"
          indicator-position="outside"
          height="100%"
          class="logo-carousel"
        >
          <el-carousel-item v-for="(slide, index) in carouselItems" :key="index">
            <div class="logo-slide">
              <div class="logo-frame">
                <el-icon :size="120" class="slide-icon">
                  <component :is="slide.icon" />
                </el-icon>
              </div>
              <h3 class="logo-title">{{ slide.title }}</h3>
              <p v-if="slide.description" class="logo-desc">{{ slide.description }}</p>
              <div v-if="slide.tags?.length" class="logo-tags">
                <span v-for="tag in slide.tags" :key="tag" class="logo-tag">{{ tag }}</span>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
      <div class="brand-decoration">
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
        <div class="decoration-circle circle-3"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  User,
  Lock,
  Monitor,
  UserFilled,
  DataAnalysis,
  Files,
  Setting,
} from '@element-plus/icons-vue'

defineOptions({ name: 'LoginView' })

const router = useRouter()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

// 记住我的 localStorage key
const REMEMBER_USERNAME_KEY = 'remember_username'

const loginForm = reactive({
  username: '',
  password: '',
  remember: false,
})

// 轮播图内容
const carouselItems = [
  {
    icon: DataAnalysis,
    title: '智能规则引擎',
    description: '强大的规则配置与管理能力，支持复杂业务逻辑',
    tags: ['规则管理', '规则集', '智能质控'],
  },
  {
    icon: Files,
    title: '批次处理',
    description: '高效的批量数据处理，快速完成质控任务',
    tags: ['批量处理', '任务管理', '结果分析'],
  },
  {
    icon: Setting,
    title: '数据管理',
    description: '完善的数据管理体系，支持多种数据源',
    tags: ['数据上传', '数据集', '数据查询'],
  },
]

// 表单验证规则
const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 从 localStorage 读取记住的用户名
const loadRememberedUsername = () => {
  const rememberedUsername = localStorage.getItem(REMEMBER_USERNAME_KEY)
  if (rememberedUsername) {
    loginForm.username = rememberedUsername
    loginForm.remember = true
  }
}

// 保存或清除记住的用户名
const handleRememberChange = (value: boolean | string | number) => {
  const remember = Boolean(value)
  if (remember) {
    if (loginForm.username) {
      localStorage.setItem(REMEMBER_USERNAME_KEY, loginForm.username)
    }
  } else {
    localStorage.removeItem(REMEMBER_USERNAME_KEY)
  }
}

// 快速登录
const quickLogin = (type: string) => {
  if (type === 'admin') {
    loginForm.username = 'admin'
    loginForm.password = 'admin'
  } else {
    loginForm.username = 'user'
    loginForm.password = 'user'
  }
  handleLogin()
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate().catch(() => {
    return false
  })

  loading.value = true

  // 模拟登录请求
  setTimeout(() => {
    loading.value = false

    // 保存登录状态
    localStorage.setItem('isLoggedIn', 'true')
    localStorage.setItem('username', loginForm.username || '用户')

    // 处理记住我
    if (loginForm.remember) {
      localStorage.setItem(REMEMBER_USERNAME_KEY, loginForm.username)
    } else {
      localStorage.removeItem(REMEMBER_USERNAME_KEY)
    }

    ElMessage.success('登录成功')

    // 跳转到工作台
    router.push('/dashboard').catch((err) => {
      if (err.name !== 'NavigationDuplicated') {
        console.error('路由跳转失败:', err)
      }
    })
  }, 500)
}

// 页面加载时读取记住的用户名
onMounted(() => {
  loadRememberedUsername()
})
</script>

<style scoped>
.login-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
  position: relative;
}

.login-left {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  padding: 40px 60px;
  position: relative;
  z-index: 2;
  clip-path: polygon(
    0% 0%,
    100% 0%,
    100% 3%,
    99.5% 6%,
    100% 10%,
    99% 15%,
    100% 20%,
    99.5% 25%,
    100% 30%,
    99% 35%,
    100% 40%,
    99.5% 45%,
    100% 50%,
    99% 55%,
    100% 60%,
    99.5% 65%,
    100% 70%,
    99% 75%,
    100% 80%,
    99.5% 85%,
    100% 90%,
    99% 93%,
    100% 96%,
    99.7% 98%,
    100% 100%,
    0% 100%
  );
}

@media (max-width: 992px) {
  .login-left {
    flex: 1;
    padding: 30px 24px;
    clip-path: none;
  }
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 60px;
  animation: slideDown 0.6s ease-out;
}

.logo-img {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}

.logo-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
  flex: 1;
  margin: 0;
}

.login-form-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 420px;
  margin: 0 auto;
  width: 100%;
  animation: fadeInUp 0.8s ease-out 0.2s backwards;
}

.form-header {
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 36px;
  font-weight: 800;
  color: #303133;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  line-height: 1.2;
  margin-top: 0;
}

.welcome-subtitle {
  font-size: 15px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.login-form {
  width: 100%;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.login-btn {
  width: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 5px;
  margin-bottom: 32px;
}

.login-btn:hover {
  transform: translateY(-2px);
}

.divider-text {
  font-size: 12px;
  color: #909399;
}

.quick-login {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.quick-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-right {
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  overflow: hidden;
  color: #ffffff;
  clip-path: polygon(
    0% 0%,
    0.3% 2%,
    0% 4%,
    0.5% 7%,
    0% 10%,
    1% 15%,
    0% 20%,
    0.5% 25%,
    0% 30%,
    1% 35%,
    0% 40%,
    0.5% 45%,
    0% 50%,
    1% 55%,
    0% 60%,
    0.5% 65%,
    0% 70%,
    1% 75%,
    0% 80%,
    0.5% 85%,
    0% 90%,
    1% 93%,
    0% 96%,
    0.3% 98%,
    0% 100%,
    100% 100%,
    100% 0%
  );
}

@media (max-width: 992px) {
  .login-right {
    display: none;
  }
}

.brand-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 70% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  animation: float 25s infinite ease-in-out alternate;
}

.brand-content {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 500px;
  height: 100%;
  display: flex;
  align-items: center;
}

.logo-carousel {
  width: 100%;
  height: 100vh;
}

:deep(.el-carousel__container) {
  height: 100%;
}

:deep(.el-carousel__item) {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-slide {
  text-align: center;
  animation: fadeInScale 0.8s ease-out;
}

.logo-frame {
  margin-bottom: 32px;
  display: inline-flex;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
  max-width: 320px;
  transition: transform 0.3s ease;
}

.logo-frame:hover {
  transform: scale(1.05);
}

.slide-icon {
  color: #ffffff;
}

.logo-slide .logo-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
  letter-spacing: 0.5px;
  color: #ffffff;
}

.logo-desc {
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 32px;
  color: rgba(255, 255, 255, 0.95);
  opacity: 0.95;
}

.logo-tags {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.logo-tag {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  transition: all 0.3s ease;
}

.logo-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.brand-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 2;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  animation: floatCircle 20s infinite ease-in-out;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  right: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: 15%;
  left: 15%;
  animation-delay: 5s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 20%;
  animation-delay: 10s;
}

/* Animations */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes floatCircle {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(20px, -20px) scale(1.1);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.85);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}
</style>
