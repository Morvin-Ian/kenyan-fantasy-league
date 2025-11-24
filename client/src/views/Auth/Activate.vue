<template>
  <div class="activation-wrapper">
    <div class="activation-card" :class="{ 'card-success': activationSuccess, 'card-error': error }">
      <div class="brand">
    
        <h1 class="title">Account Activation</h1>
      </div>

      <transition name="fade-scale">
        <div v-if="authStore.isLoading" class="state-container">
          <div class="loading-spinner">
            <svg viewBox="0 0 50 50" class="spinner">
              <circle cx="25" cy="25" r="20" fill="none" stroke-width="5" stroke-linecap="round" class="path"></circle>
            </svg>
          </div>
          <p class="status-text">Verifying your account</p>
          <div class="progress-dots">
            <span></span><span></span><span></span>
          </div>
          <p class="sub-text">This may take a few moments</p>
        </div>
      </transition>

      <!-- Success State -->
      <transition name="fade-scale">
        <div v-if="activationSuccess" class="state-container">
          <div class="status-icon success">
            <svg viewBox="0 0 24 24" class="icon">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" 
                fill="none" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" 
                fill="none" stroke-width="2" 
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h2 class="status-title success">Activation Complete</h2>
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
              <circle cx="12" cy="12" r="10" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
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
      
      <div class="card-footer" v-if="!authStore.isLoading && !activationSuccess && !error">
        <p class="footer-text">If you need assistance, contact our <a href="#" class="text-link">support team</a></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from "vue-router";

const router = useRouter();

const route = useRoute()
const authStore = useAuthStore()

const error = ref('')
const activationSuccess = ref(false)

async function activateAccount() {
  const { uid, token } = route.params

  if (!uid || !token) {
    error.value = 'Invalid activation link. Please request a new one.'
    return
  }

  try {
    error.value = ''
    await authStore.activateAccount(uid, token)
    activationSuccess.value = true
  } catch (err) {
    error.value = 'We couldn\'t activate your account. Please try again or contact support.'
  } finally {
  }
}


onMounted(() => {
  if (authStore.isAuthenticated) {
    router.replace({ name: "home" });
  }
  authStore.error = null;
  activateAccount()
})
</script>

<style scoped>
.activation-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: radial-gradient(ellipse at top, #f0f4f8 0%, #d9e2ec 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.activation-card {
  background: white;
  border-radius: 24px;
  padding: 3rem;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.card-success {
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  box-shadow: 0 20px 25px -5px rgba(0, 120, 50, 0.1),
              0 10px 10px -5px rgba(0, 120, 50, 0.04);
}

.card-error {
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
  box-shadow: 0 20px 25px -5px rgba(220, 38, 38, 0.1),
              0 10px 10px -5px rgba(220, 38, 38, 0.04);
}

.brand {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-circle {
  width: 72px;
  height: 72px;
  margin: 0 auto 1.25rem;
  background: #f3f4f6;
  border-radius: 20px;
  display: grid;
  place-items: center;
  transform: rotate(45deg);
  transition: all 0.5s ease;
}

.card-success .logo-circle {
  background: #dcfce7;
}

.card-error .logo-circle {
  background: #fee2e2;
}

.brand-logo {
  width: 36px;
  height: 36px;
  color: #4b5563;
  transform: rotate(-45deg);
}

.card-success .brand-logo {
  color: #15803d;
}

.card-error .brand-logo {
  color: #dc2626;
}

.title {
  color: #111827;
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  margin: 0;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 0;
}

/* Loading Animation */
.loading-spinner {
  display: inline-block;
  width: 80px;
  height: 80px;
}

.spinner {
  animation: rotate 2s linear infinite;
  transform-origin: center center;
  width: 100%;
  height: 100%;
}

.path {
  stroke: #6366f1;
  stroke-dasharray: 89, 200;
  stroke-dashoffset: 0;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% { transform: rotate(360deg); }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

.progress-dots {
  display: flex;
  gap: 0.5rem;
}

.progress-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d1d5db;
  display: inline-block;
  animation: dotFade 1.4s infinite ease-in-out both;
}

.progress-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.progress-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes dotFade {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* Status Icons */
.status-icon {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -2px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 10;
}

.status-icon.success {
  background: #dcfce7;
  color: #15803d;
}

.status-icon.success:before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #15803d;
  opacity: 0.15;
  z-index: -1;
  animation: pulse 2s infinite;
}

.status-icon.error {
  background: #fee2e2;
  color: #dc2626;
}

.status-icon.error:before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #dc2626;
  opacity: 0.15;
  z-index: -1;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.15); opacity: 0.1; }
  100% { transform: scale(1); opacity: 0.3; }
}

.icon {
  width: 40px;
  height: 40px;
}

/* Text Styles */
.status-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.025em;
}

.status-title.success {
  color: #15803d;
}

.status-title.error {
  color: #dc2626;
}

.status-text {
  color: #4b5563;
  font-size: 1.25rem;
  font-weight: 500;
  text-align: center;
  margin: 0;
}

.sub-text {
  color: #6b7280;
  font-size: 0.875rem;
  margin: -0.5rem 0 0;
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
  padding: 0.875rem 1.75rem;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  margin-top: 1.5rem;
  border: none;
  cursor: pointer;
  text-decoration: none;
  font-size: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
              0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.action-button.success {
  background: #15803d;
  color: white;
}

.action-button.success:hover {
  background: #166534;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.action-button.error {
  background: #dc2626;
  color: white;
}

.action-button.error:hover {
  background: #b91c1c;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(220, 38, 38, 0.2),
              0 4px 6px -2px rgba(220, 38, 38, 0.1);
}

.button-icon {
  width: 18px;
  height: 18px;
}

.support-link {
  color: #6b7280;
  text-decoration: none;
  font-size: 0.875rem;
  margin-top: 1rem;
  transition: color 0.2s ease;
}

.support-link:hover {
  color: #4b5563;
  text-decoration: underline;
}

.card-footer {
  margin-top: 2rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

.text-link {
  color: #6366f1;
  text-decoration: none;
  transition: color 0.2s ease;
}

.text-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* Transitions */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.94);
}

@media (max-width: 640px) {
  .activation-card {
    padding: 2.5rem 1.5rem;
  }

  .title {
    font-size: 1.75rem;
  }

  .status-title {
    font-size: 1.5rem;
  }

  .status-text {
    font-size: 1.125rem;
  }
  
  .status-icon {
    width: 72px;
    height: 72px;
  }
  
  .icon {
    width: 32px;
    height: 32px;
  }
}
</style>