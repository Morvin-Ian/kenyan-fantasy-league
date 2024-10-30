<template>
    <div class="activation-container">
      <div class="activation-card">
        <h1>Account Activation</h1>
  
        <!-- Loading State -->
        <div v-if="loading" class="state-container">
          <div class="loader"></div>
          <p>Activating your account...</p>
        </div>
  
        <!-- Success State -->
        <div v-if="activationSuccess" class="state-container">
          <div class="icon-circle success">
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h2>Account Activated!</h2>
          <p>Your account has been successfully activated.</p>
          <router-link to="/sign-in" class="button">
            Proceed to Login
          </router-link>
        </div>
  
        <!-- Error State -->
        <div v-if="error" class="state-container">
          <div class="icon-circle error">
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h2>Activation Failed</h2>
          <p class="error-text">{{ error }}</p>
          <button @click="activateAccount" class="button">
            Retry Activation
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth';

  import axios from 'axios'
  
  const route = useRoute()
  const router = useRouter()
  const authStore = useAuthStore()
  
  const loading = ref(true)
  const error = ref(null)
  const activationSuccess = ref(false)
    
  async function activateAccount() {
    const { uid, token } = route.params
  
    if (!uid || !token) {
      error.value = 'Invalid activation link. Please check your email for the correct link.'
      loading.value = false
      return
    }
  
    try {
      // Send POST request with uid and token
      await authStore.activateAccount(uid, token)  
      loading.value = false
      activationSuccess.value = true
    } catch (err) {
      loading.value = false
      error.value = err.response?.data?.message || 
        'An error occurred during account activation. Please try again.'
    }
  }
  
  onMounted(() => {
    activateAccount()
  })
  </script>
  
  <style scoped>
  .activation-container {
    display: flex;
    min-height: 100vh;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #dbdbdb 0%, #ffffff 100%);
    padding: 20px;
    color: #ffffff;
  }
  
  .activation-card {
    background: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    width: 100%;
    max-width: 420px;
    text-align: center;
    transition: transform 0.3s ease-in-out;
  }
  
  .activation-card:hover {
    transform: scale(1.02);
  }
  
  h1 {
    color: #1b5e20;
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
    font-weight: bold;
  }
  
  h2 {
    color: #1b5e20;
    font-size: 1.35rem;
    margin: 1rem 0;
    font-weight: 600;
  }
  
  p {
    color: #424242;
    margin: 0.5rem 0;
    font-size: 1rem;
  }
  
  .state-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .loader {
    width: 50px;
    height: 50px;
    border: 4px solid #ffffff;
    border-top: 4px solid #0288d1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .icon-circle {
    width: 68px;
    height: 68px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
  }
  
  .icon-circle.success {
    background-color: #c8e6c9;
  }
  
  .icon-circle.error {
    background-color: #ffcdd2;
  }
  
  .icon {
    width: 34px;
    height: 34px;
    stroke: currentColor;
    stroke-width: 2;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  
  .success .icon {
    color: #2e7d32;
  }
  
  .error .icon {
    color: #d32f2f;
  }
  
  .button {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    margin-top: 1rem;
    background-color: #0288d1;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    font-size: 1rem;
    transition: background-color 0.3s, transform 0.2s;
  }
  
  .button:hover {
    background-color: #0277bd;
    transform: translateY(-2px);
  }
  
  .error-text {
    color: #d32f2f;
    font-weight: 500;
  }
  </style>
  