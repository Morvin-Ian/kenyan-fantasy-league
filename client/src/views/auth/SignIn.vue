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
              <CheckCircle v-if="!v$.email.$error" class="valid-icon h-4" />
              <XCircle v-else class="invalid-icon h-4 text-red-400" />
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
import { onMounted } from 'vue';

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
onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) {
    router.replace({ name: 'home' });
  }
});
</script>

<style scoped>
.signin-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f4f8, #ffffff);
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}

.signin-card {
  background: #ffffff;
  padding: 2rem;
  border-radius: 1rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0px 12px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
}

/* Header */
.logo {
  font-size: 1.75rem;
  font-weight: bold;
  color: #1a472a;
  margin-bottom: 1.5rem;
}

/* Form Group */
.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
  display: block;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.input-wrapper .toggle-password {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
}

.error-text {
  font-size: 0.8rem;
  color: #ef4444;
  margin-top: 0.5rem;
}

/* Buttons */
.submit-button {
  width: 100%;
  padding: 0.8rem;
  background: #1a472a;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-button:hover {
  background: #164624;
}

.submit-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.register-link {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #6b7280;
}

.register-link a {
  color: #1a472a;
  font-weight: bold;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

/* Error Alert */
.error-alert {
  background: #fee2e2;
  color: #b91c1c;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
