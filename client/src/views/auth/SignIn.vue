<template>
    <div class="signin-container">
      <div class="signin-card">
        <div class="header">
          <div class="logo">Fantasy Kenyan League</div>
        </div>
  
        <div v-if="authStore.error" class="error-alert">
          <AlertCircle class="alert-icon" />
          <p>{{ authStore.error }}</p>
        </div>
  
        <form @submit.prevent="handleSubmit" class="signin-form" novalidate>
          <div class="form-group">
            <label for="email">Email address</label>
            <div class="input-wrapper">
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                placeholder="Enter your email"
                :class="{ 'error': v$.email.$error }"
                @blur="v$.email.$touch"
              />
              <div class="input-icon" v-if="form.email">
                <CheckCircle v-if="!v$.email.$error" class="valid-icon" />
                <XCircle v-else class="invalid-icon" />
              </div>
            </div>
            <span v-if="v$.email.$error" class="error-text">
              {{ v$.email.$errors[0].$message }}
            </span>
          </div>
  
          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-wrapper">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Enter your password"
                :class="{ 'error': v$.password.$error }"
                @blur="v$.password.$touch"
              />
              <button 
                type="button" 
                class="toggle-password"
                @click="showPassword = !showPassword"
              >
                <Eye v-if="!showPassword" />
                <EyeOff v-else />
              </button>
            </div>
            <span v-if="v$.password.$error" class="error-text">
              {{ v$.password.$errors[0].$message }}
            </span>
          </div>
  
          <button
            type="submit"
            :disabled="authStore.isLoading || !formIsValid"
            class="submit-button"
          >
            <span v-if="authStore.isLoading" class="loading-spinner"></span>
            <span v-else>Sign In</span>
          </button>
  
          <p class="register-link">
            Don't have an account?
            <router-link to="/sign-up">Create one</router-link>
          </p>
        </form>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import { AlertCircle, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-vue-next';
  import { useAuthStore } from '@/stores/auth';
  import useVuelidate from '@vuelidate/core';
  import { required, email } from '@vuelidate/validators';
  
  const router = useRouter();
  const authStore = useAuthStore();
  
  const showPassword = ref(false);
  
  const form = reactive({
    email: '',
    password: '',
  });
  
  const rules = {
    email: { required, email },
    password: { required },
  };
  
  const v$ = useVuelidate(rules, form);
  
  const formIsValid = computed(() => !v$.value.$error);
  
  const handleSubmit = async () => {
    const isFormValid = await v$.value.$validate();
    
    if (!isFormValid || !formIsValid.value) return;
  
    try {
      await authStore.login({ email: form.email, password: form.password });
      router.push({ path: '/' });
    } catch (error) {
      console.error('Sign-in failed:', error);
    }
  };
  </script>
  
  <style scoped>
  .signin-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: linear-gradient(135deg, #dbdbdb 0%, #ffffff 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  .signin-card {
    width: 100%;
    max-width: 480px;
    background: white;
    border-radius: 1.25rem;
    padding: 2.5rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
                0 10px 10px -5px rgba(0, 0, 0, 0.04);
    transition: transform 0.3s ease;
  }
  
  .signin-card:hover {
    transform: translateY(-2px);
  }
  
  .logo {
    font-size: 2rem;
    font-weight: 700;
    color: #1a472a;
    text-align: center;
    margin-bottom: 1.25rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .header {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  
  .header h2 {
    font-size: 1.75rem;
    color: #1a472a;
    margin: 0 0 0.75rem 0;
    font-weight: 600;
  }
  
  .header p {
    color: #6b7280;
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;
  }
  
  .error-alert {
    display: flex;
    align-items: center;
    background: #fee2e2;
    border-left: 4px solid #ef4444;
    padding: 1rem;
    margin-bottom: 1.5rem;
    border-radius: 0.5rem;
    animation: slideIn 0.3s ease;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
    position: relative;
  }
  
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-size: 0.875rem;
    font-weight: 500;
    transition: color 0.2s ease;
  }
  
  .form-group input {
    width: 100%;
    padding: 0.875rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 1rem;
  }
  
  .input-icon {
    position: absolute;
    right: 1rem;
    color: #6b7280;
  }
  
  .toggle-password {
    background: none;
    border: none;
    position: absolute;
    right: 1rem;
    color: #6b7280;
    cursor: pointer;
  }
  
  .error-text {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  .submit-button {
    width: 100%;
    padding: 0.875rem 1rem;
    background: #1a472a;
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  
  .submit-button:disabled {
    background: #d1d5db;
    cursor: not-allowed;
  }
  
  .loading-spinner {
    border: 2px solid #fff;
    border-radius: 50%;
    border-top: 2px solid transparent;
    width: 1rem;
    height: 1rem;
    animation: spin 0.6s linear infinite;
  }
  
  .register-link {
    text-align: center;
    margin-top: 1.5rem;
    color: #374151;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  </style>
  