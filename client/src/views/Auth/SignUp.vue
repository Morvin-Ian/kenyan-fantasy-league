<template>
  <div class="register-container">
    <div class="register-card">
      <div class="header">
        <h1 class="logo">Fantasy Kenyan League</h1>
        <p>Join the Kenyan Premier League Fantasy community</p>
      </div>

      <div v-if="authStore.error" class="error-alert">
        <AlertCircle class="alert-icon" />
        <p>{{ authStore.error }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="register-form" novalidate>
        <!-- Name fields in a row -->
        <div class="name-row">
          <div class="form-group">
            <label for="username">Username</label>
            <input id="username" v-model="form.username" type="text" required placeholder="Choose a username"
              :class="{ error: v$.username.$error }" @blur="v$.username.$touch" />
            <span v-if="v$.username.$error" class="error-text">
              {{ v$.username.$errors[0].$message }}
            </span>
          </div>

          <div class="form-group">
            <label for="email">Email address</label>
            <input id="email" v-model="form.email" type="email" required placeholder="your@email.com"
              :class="{ error: v$.email.$error }" @blur="v$.email.$touch" />
            <span v-if="v$.email.$error" class="error-text">
              {{ v$.email.$errors[0].$message }}
            </span>
          </div>
        </div>

        <!-- Password field -->
        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input">
            <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" required
              placeholder="Create a password" :class="{ error: v$.password.$error }" @blur="v$.password.$touch" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" />
              <EyeOff v-else />
            </button>
          </div>
          <span v-if="v$.password.$error" class="error-text">
            {{ v$.password.$errors[0].$message }}
          </span>

          <!-- Password strength indicator (optional visual feedback) -->
          <div class="password-strength" v-if="form.password">
            <div class="strength-meter">
              <div class="strength-bar" :style="{ width: `${passwordStrength}%` }" :class="strengthClass"></div>
            </div>
            <span class="strength-text" :class="strengthClass">{{ passwordStrengthText }}</span>
          </div>
        </div>

        <!-- Confirm Password field -->
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <div class="password-input">
            <input id="confirmPassword" v-model="form.confirmPassword" :type="showConfirmPassword ? 'text' : 'password'"
              required placeholder="Confirm your password" :class="{ error: v$.confirmPassword.$error }"
              @blur="v$.confirmPassword.$touch" />
            <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
              <Eye v-if="!showConfirmPassword" />
              <EyeOff v-else />
            </button>
          </div>
          <span v-if="v$.confirmPassword.$error" class="error-text">
            {{ v$.confirmPassword.$errors[0].$message }}
          </span>
        </div>

        <!-- Password requirements (now optional visual guide) -->
        <div class="password-requirements" v-if="form.password">
          <p class="requirements-title">Password Strength Guide (Optional)</p>
          <div class="requirements-grid">
            <div class="requirement" :class="{ met: hasLength }">
              <span class="check-icon">{{ hasLength ? '✓' : '○' }}</span>
              <span>8+ characters</span>
            </div>
            <div class="requirement" :class="{ met: hasUpperCase }">
              <span class="check-icon">{{ hasUpperCase ? '✓' : '○' }}</span>
              <span>Uppercase</span>
            </div>
            <div class="requirement" :class="{ met: hasLowerCase }">
              <span class="check-icon">{{ hasLowerCase ? '✓' : '○' }}</span>
              <span>Lowercase</span>
            </div>
            <div class="requirement" :class="{ met: hasNumber }">
              <span class="check-icon">{{ hasNumber ? '✓' : '○' }}</span>
              <span>Number</span>
            </div>
            <div class="requirement" :class="{ met: hasSpecial }">
              <span class="check-icon">{{ hasSpecial ? '✓' : '○' }}</span>
              <span>Special char</span>
            </div>
          </div>
        </div>

        <!-- Terms checkbox -->
        <div class="terms-section">
          <label class="terms-checkbox">
            <input v-model="form.acceptTerms" type="checkbox" required @blur="v$.acceptTerms.$touch" />
            <span class="checkbox-text">
              I agree to the
              <a href="/terms" class="terms-link">Terms of Service</a>
              and
              <a href="/privacy" class="terms-link">Privacy Policy</a>
            </span>
          </label>
          <span v-if="v$.acceptTerms.$error" class="error-text">
            You must accept the terms to continue
          </span>
        </div>

        <!-- Submit button -->
        <button type="submit" :disabled="authStore.isLoading || !formIsValid" class="submit-button">
          <span v-if="authStore.isLoading" class="loading-spinner"></span>
          <span v-else>Create Account</span>
        </button>

        <div class="divider">
          <span>or</span>
        </div>

        <button type="button" @click="handleGoogleSignIn" :disabled="authStore.isLoading" class="google-button">
          <svg class="google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4" />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853" />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05" />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335" />
          </svg>
          <span>Continue with Google</span>
        </button>

        <p class="login-link">
          Already have an account?
          <router-link to="/sign-in">Sign in</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { AlertCircle, Eye, EyeOff } from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "vue-toastification";
import useVuelidate from "@vuelidate/core";
import {
  required,
  email,
  minLength,
  maxLength,
  helpers,
} from "@vuelidate/validators";
import { onMounted } from "vue";

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const showPassword = ref(false);
const showConfirmPassword = ref(false);

const form = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  acceptTerms: false,
});

// Name validator
const nameValidator = helpers.regex(/^[a-zA-Z\s-']+$/);

// Username validator (allows letters, numbers, underscores, hyphens)
const usernameValidator = helpers.regex(/^[a-zA-Z0-9_-]+$/);

const rules = {
  username: {
    required,
    minLength: minLength(3),
    maxLength: maxLength(20),
    validUsername: helpers.withMessage(
      "Username can only contain letters, numbers, underscores and hyphens",
      usernameValidator
    ),
  },
  email: { required, email },
  password: {
    required,
    minLength: minLength(8),
  },
  confirmPassword: {
    required,
    sameAsPassword: helpers.withMessage(
      "Passwords must match",
      (value) => value === form.password
    ),
  },
  acceptTerms: { required },
};

const v$ = useVuelidate(rules, form);

// Password strength indicators
const hasLength = computed(() => form.password.length >= 8);
const hasUpperCase = computed(() => /[A-Z]/.test(form.password));
const hasLowerCase = computed(() => /[a-z]/.test(form.password));
const hasNumber = computed(() => /\d/.test(form.password));
const hasSpecial = computed(() => /[@$!%*?&]/.test(form.password));

const passwordStrength = computed(() => {
  let strength = 0;
  if (hasLength.value) strength += 20;
  if (hasUpperCase.value) strength += 20;
  if (hasLowerCase.value) strength += 20;
  if (hasNumber.value) strength += 20;
  if (hasSpecial.value) strength += 20;
  return strength;
});

const strengthClass = computed(() => {
  if (passwordStrength.value <= 20) return "weak";
  if (passwordStrength.value <= 60) return "medium";
  return "strong";
});

const passwordStrengthText = computed(() => {
  if (passwordStrength.value <= 20) return "Weak";
  if (passwordStrength.value <= 60) return "Medium";
  return "Strong";
});

const formIsValid = computed(() => {
  return !v$.value.$error && form.acceptTerms;
});

const handleSubmit = async () => {
  const isFormValid = await v$.value.$validate();

  if (!isFormValid || !formIsValid.value) return;

  try {
    await authStore.register({
      first_name: null,
      last_name: null,
      username: form.username,
      email: form.email,
      password: form.password,
      re_password: form.confirmPassword,
    });

    if (!authStore.error) {
      toast.success(
        "Successful registration! Please check your email to activate your account.",
        {
          timeout: 10000,
        }
      );
      router.push({ path: "/sign-in" });
    }
  } catch (error: any) {
    console.error("Registration failed:", error);
    // Error is already set in store, loading state is already cleared
  }
};

// Google Sign-In Handler - Redirect to backend
const handleGoogleSignIn = () => {
  window.location.href = `/api/v1/auth/google/login/`;
};

onMounted(() => {
  authStore.error = null;
  if (authStore.isAuthenticated) {
    router.replace({ name: "home" });
  }
});
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f4f8, #e0f2f1);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a472a;
  margin-bottom: 0.5rem;
}

.header p {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.name-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
  margin-bottom: 0.375rem;
}

.form-group input,
.password-input {
  position: relative;
}

input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #f8fafc;
}

input:focus {
  outline: none;
  border-color: #1a472a;
  box-shadow: 0 0 0 2px rgba(26, 71, 42, 0.1);
  background: white;
}

input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.error-text {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.375rem;
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
}

.password-strength {
  margin-top: 0.75rem;
}

.strength-meter {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-bar.weak {
  background: #ef4444;
}

.strength-bar.medium {
  background: #f59e0b;
}

.strength-bar.strong {
  background: #10b981;
}

.strength-text {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

.strength-text.weak {
  color: #ef4444;
}

.strength-text.medium {
  color: #f59e0b;
}

.strength-text.strong {
  color: #10b981;
}

.password-requirements {
  margin-top: 0.5rem;
  background: #f8fafc;
  border-radius: 10px;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
}

.requirements-title {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  font-style: italic;
}

.requirements-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #64748b;
  transition: all 0.2s;
}

.requirement.met {
  color: #10b981;
  font-weight: 500;
}

.check-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
}

.terms-section {
  margin-top: 0.5rem;
}

.terms-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #475569;
}

.terms-checkbox input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  margin-top: 0.125rem;
}

.terms-link {
  color: #1a472a;
  font-weight: 500;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

.submit-button {
  margin-top: 0.5rem;
  width: 100%;
  padding: 0.875rem;
  background: #1a472a;
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.submit-button:hover {
  background: #164624;
  transform: translateY(-1px);
}

.submit-button:active {
  transform: translateY(0);
}

.submit-button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  display: inline-block;
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  margin: 1rem 0;
  color: #9ca3af;
  font-size: 0.85rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e5e7eb;
}

.divider span {
  padding: 0 1rem;
}

/* Google Button */
.google-button {
  width: 100%;
  padding: 0.875rem;
  background: #ffffff;
  color: #3c4043;
  font-weight: 500;
  border: 1.5px solid #dadce0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
}

.google-button:hover {
  background: #f8f9fa;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.google-button:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.google-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #64748b;
}

.login-link a {
  color: #1a472a;
  font-weight: 600;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fee2e2;
  color: #b91c1c;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .register-container {
    padding: 1rem;
  }

  .register-card {
    padding: 1.5rem;
  }

  .name-row {
    grid-template-columns: 1fr;
  }

  .requirements-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>