<template>
  <div class="activation-wrapper">
    <div class="activation-card" :class="{ 'card-success': activationSuccess, 'card-error': error }">
      <div class="brand">
        <h1 class="title">Account Activation</h1>
      </div>

      <!-- Loading State -->
      <transition name="fade-scale">
        <div v-if="loading" class="state-container">
          <div class="loading-ring">
            <div></div><div></div><div></div><div></div>
          </div>
          <p class="status-text">Verifying your account...</p>
          <p class="sub-text">This may take a few moments</p>
        </div>
      </transition>

      <!-- Success State -->
      <transition name="fade-scale">
        <div v-if="activationSuccess" class="state-container">
          <div class="status-icon success">
            <svg viewBox="0 0 24 24" class="icon">
              <path d="M20 6L9 17l-5-5" stroke="currentColor" 
                fill="none" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h2 class="status-title success">Activation Complete!</h2>
          <p class="status-text">Your account has been successfully verified</p>
          <router-link to="/sign-in" class="action-button success">
            Continue to Login
            <svg class="button-icon" viewBox="0 0 24 24">
              <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" 
                fill="none" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </router-link>
        </div>
      </transition>

      <!-- Error State -->
      <transition name="fade-scale">
        <div v-if="error" class="state-container">
          <div class="status-icon error">
            <svg viewBox="0 0 24 24" class="icon">
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                stroke="currentColor" fill="none" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h2 class="status-title error">Activation Failed</h2>
          <p class="error-message">{{ error }}</p>
          <button @click="activateAccount" class="action-button error">
            Try Again
            <svg class="button-icon" viewBox="0 0 24 24">
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                stroke="currentColor" fill="none" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const activationSuccess = ref(false)

async function activateAccount() {
  const { uid, token } = route.params

  if (!uid || !token) {
    error.value = 'Invalid activation link. Please request a new one.'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = ''
    await authStore.activateAccount(uid, token)
    activationSuccess.value = true
  } catch (err) {
    error.value = 'We couldn\'t activate your account. Please try again or contact support.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  activateAccount()
})
</script>

<style scoped>
.activation-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}

.activation-card {
  background: white;
  border-radius: 24px;
  padding: 2.5rem;
  width: 100%;
  max-width: 460px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05),
              0 8px 10px -6px rgba(0, 0, 0, 0.02);
  transition: all 0.4s ease;
}

.card-success {
  background: linear-gradient(to bottom right, #f0fdf4, #ffffff);
}

.card-error {
  background: linear-gradient(to bottom right, #fef2f2, #ffffff);
}

.brand {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-circle {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  background: #f3f4f6;
  border-radius: 16px;
  display: grid;
  place-items: center;
}

.brand-logo {
  width: 32px;
  height: 32px;
  color: #4b5563;
}

.title {
  color: #111827;
  font-size: 1.875rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

/* Loading Animation */
.loading-ring {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}

.loading-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 48px;
  height: 48px;
  margin: 8px;
  border: 4px solid #6366f1;
  border-radius: 50%;
  animation: loading-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: #6366f1 transparent transparent transparent;
}

.loading-ring div:nth-child(1) { animation-delay: -0.45s; }
.loading-ring div:nth-child(2) { animation-delay: -0.3s; }
.loading-ring div:nth-child(3) { animation-delay: -0.15s; }

@keyframes loading-ring {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Status Icons */
.status-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: grid;
  place-items: center;
}

.status-icon.success {
  background: #dcfce7;
  color: #15803d;
}

.status-icon.error {
  background: #fee2e2;
  color: #dc2626;
}

.icon {
  width: 32px;
  height: 32px;
}

/* Text Styles */
.status-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0.5rem 0;
}

.status-title.success {
  color: #15803d;
}

.status-title.error {
  color: #dc2626;
}

.status-text {
  color: #4b5563;
  font-size: 1.125rem;
}

.sub-text {
  color: #6b7280;
  font-size: 0.875rem;
}

.error-message {
  color: #991b1b;
  text-align: center;
  font-size: 1rem;
  max-width: 280px;
  margin: 0 auto;
}

/* Button Styles */
.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-weight: 500;
  transition: all 0.2s ease;
  margin-top: 1rem;
  border: none;
  cursor: pointer;
  text-decoration: none;
  font-size: 1rem;
}

.action-button.success {
  background: #15803d;
  color: white;
}

.action-button.success:hover {
  background: #166534;
  transform: translateY(-2px);
}

.action-button.error {
  background: #dc2626;
  color: white;
}

.action-button.error:hover {
  background: #b91c1c;
  transform: translateY(-2px);
}

.button-icon {
  width: 18px;
  height: 18px;
}

/* Transitions */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.4s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

@media (max-width: 640px) {
  .activation-card {
    padding: 2rem;
  }

  .title {
    font-size: 1.5rem;
  }

  .status-title {
    font-size: 1.25rem;
  }

  .status-text {
    font-size: 1rem;
  }
}
</style>