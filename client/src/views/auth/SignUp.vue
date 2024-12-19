<template>
  <div class="register-container">
    <div class="register-card">
      <div class="header">
        <div class="logo">Fantasy Kenyan League</div>
        <p style="font-size:small">Join the Kenyan Premier League Fantasy community</p>
      </div>

      <div v-if="authStore.error" class="error-alert">
        <AlertCircle class="alert-icon" />
        <p>{{ authStore.error }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="register-form" novalidate>
        <!-- First Name field -->
        <div class="form-group">
          <label for="firstName">First Name</label>
          <div class="input-wrapper">
            <input id="firstName" v-model="form.firstName" type="text" required placeholder="Enter your first name"
              :class="{ 'error': v$.firstName.$error }" @blur="v$.firstName.$touch" />
            <div class="input-icon" v-if="form.firstName">
              <CheckCircle v-if="!v$.firstName.$error" class="valid-icon h-4" />
              <XCircle v-else class="invalid-icon h-4 text-red-400" />
            </div>
          </div>
          <span v-if="v$.firstName.$error" class="error-text">
            {{ v$.firstName.$errors[0].$message }}
          </span>
        </div>

        <!-- Last Name field -->
        <div class="form-group">
          <label for="lastName">Last Name</label>
          <div class="input-wrapper">
            <input id="lastName" v-model="form.lastName" type="text" required placeholder="Enter your last name"
              :class="{ 'error': v$.lastName.$error }" @blur="v$.lastName.$touch" />
            <div class="input-icon" v-if="form.lastName">
              <CheckCircle v-if="!v$.lastName.$error" class="valid-icon h4" />
              <XCircle v-else class="invalid-icon h-4 text-red-400" />
            </div>
          </div>
          <span v-if="v$.lastName.$error" class="error-text">
            {{ v$.lastName.$errors[0].$message }}
          </span>
        </div>

        <div class="form-group">
          <label for="email">Email address</label>
          <div class="input-wrapper">
            <input id="email" v-model="form.email" type="email" required placeholder="Enter your email"
              :class="{ 'error': v$.email.$error }" @blur="v$.email.$touch" />
            <div class="input-icon" v-if="form.email">
              <CheckCircle v-if="!v$.email.$error" class="valid-icon h-4" />
              <XCircle v-else class="invalid-icon h-4 text-red-400" />
            </div>
          </div>
          <span v-if="v$.email.$error" class="error-text">
            {{ v$.email.$errors[0].$message }}
          </span>
        </div>

        <div class="password-section">
          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-wrapper">
              <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" required
                placeholder="Create a password" :class="{ 'error': v$.password.$error }" @blur="v$.password.$touch" />
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                <Eye v-if="!showPassword" />
                <EyeOff v-else />
              </button>
            </div>
            <span v-if="v$.password.$error" class="error-text">
              {{ v$.password.$errors[0].$message }}
            </span>
          </div>

          <div class="password-strength" v-if="form.password">
            <div class="strength-meter">
              <div class="strength-bar" :style="{ width: `${passwordStrength}%` }" :class="strengthClass"></div>
            </div>
            <span class="strength-text" :class="strengthClass">
              {{ passwordStrengthText }}
            </span>
          </div>

          <div class="password-requirements">
            <p>Password must contain:</p>
            <ul>
              <li :class="{ 'met': hasLength }">At least 8 characters</li>
              <li :class="{ 'met': hasUpperCase }">One uppercase letter</li>
              <li :class="{ 'met': hasLowerCase }">One lowercase letter</li>
              <li :class="{ 'met': hasNumber }">One number</li>
              <li :class="{ 'met': hasSpecial }">One special character</li>
            </ul>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <div class="input-wrapper">
            <input id="confirmPassword" v-model="form.confirmPassword" :type="showConfirmPassword ? 'text' : 'password'"
              required placeholder="Confirm your password" :class="{ 'error': v$.confirmPassword.$error }"
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

        <div class="terms-section">
          <label class="terms-checkbox">
            <input v-model="form.acceptTerms" type="checkbox" required @blur="v$.acceptTerms.$touch" />
            <span class="checkbox-text">
              I agree to the <a href="/terms" class="terms-link">Terms of Service</a> and
              <a href="/privacy" class="terms-link">Privacy Policy</a>
            </span>
          </label>
          <span v-if="v$.acceptTerms.$error" class="error-text">
            You must accept the terms to continue
          </span>
        </div>

        <button type="submit" :disabled="authStore.isLoading || !formIsValid" class="submit-button">
          <span v-if="authStore.isLoading" class="loading-spinner"></span>
          <span v-else>Create Account</span>
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
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { AlertCircle, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';
import { useToast } from "vue-toastification";
import useVuelidate from '@vuelidate/core';
import { required, email, minLength, maxLength, helpers } from '@vuelidate/validators';
import { onMounted } from 'vue';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const showPassword = ref(false);
const showConfirmPassword = ref(false);


const form = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false,
});

// Custom password validator
const strongPassword = helpers.regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/);

// Name validator
const nameValidator = helpers.regex(/^[a-zA-Z\s-']+$/);

const rules = {
  firstName: {
    required,
    minLength: minLength(2),
    maxLength: maxLength(20),
    validName: helpers.withMessage(
      'First name can only contain letters, spaces, hyphens and apostrophes',
      nameValidator
    )
  },
  lastName: {
    required,
    minLength: minLength(2),
    maxLength: maxLength(20),
    validName: helpers.withMessage(
      'Last name can only contain letters, spaces, hyphens and apostrophes',
      nameValidator
    )
  },
  email: { required, email },
  password: {
    required,
    minLength: minLength(8),
    strongPassword
  },
  confirmPassword: {
    required,
    sameAsPassword: helpers.withMessage(
      'Passwords must match',
      (value) => value === form.password
    )
  },
  acceptTerms: { required }
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
  if (passwordStrength.value <= 20) return 'weak';
  if (passwordStrength.value <= 60) return 'medium';
  return 'strong';
});

const passwordStrengthText = computed(() => {
  if (passwordStrength.value <= 20) return 'Weak';
  if (passwordStrength.value <= 60) return 'Medium';
  return 'Strong';
});

const formIsValid = computed(() => {
  return !v$.value.$error && form.acceptTerms && passwordStrength.value >= 80;
});

const handleSubmit = async () => {
  const isFormValid = await v$.value.$validate();

  if (!isFormValid || !formIsValid.value) return;

  try {
    await authStore.register({
      first_name: form.firstName,
      last_name: form.lastName,
      username: form.lastName,
      email: form.email,
      password: form.password,
      re_password: form.confirmPassword,
    });

    toast.success("🎉 Activation email sent! Please check your inbox to complete your registration", {
      timeout: 10000
    });
    router.push({ path: '/sign-in' });

  } catch (error) {
    console.error('Registration failed:', error);
  }
};

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.replace({ name: 'home' }); 
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
  background: linear-gradient(135deg, #dbdbdb 0%, #ffffff 100%);
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}

.register-card {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 1.25rem;
  padding: 2.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transition: transform 0.3s ease;
}

.register-card:hover {
  transform: translateY(-2px);
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a472a;
  text-align: center;
  margin-bottom: 1.25rem;
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

.form-group {
  margin-bottom: 1.5rem;
  position: relative;
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


.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.form-group:focus-within label {
  color: #1a472a;
}

.form-group input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: #f9fafb;
}

.form-group input:hover {
  border-color: #d1d5db;
}

.form-group input:focus {
  outline: none;
  border-color: #1a472a;
  box-shadow: 0 0 0 3px rgba(26, 71, 42, 0.1);
  background: white;
}

.form-group input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.error-text {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.5rem;
  display: block;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.password-strength {
  margin-top: 1rem;
}

.strength-meter {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-bar.weak {
  background: #ef4444;
  animation: pulse 2s infinite;
}

.strength-bar.medium {
  background: #f59e0b;
}

.strength-bar.strong {
  background: #059669;
  animation: celebrate 0.5s ease;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }

  50% {
    opacity: 0.7;
  }

  100% {
    opacity: 1;
  }
}

@keyframes celebrate {
  0% {
    transform: scaleX(0.8);
  }

  50% {
    transform: scaleX(1.1);
  }

  100% {
    transform: scaleX(1);
  }
}

.strength-text {
  font-size: 0.75rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

.password-requirements {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
}

.password-requirements p {
  font-size: 0.75rem;
  color: #374151;
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.375rem;
}

.password-requirements li {
  font-size: 0.75rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  transition: color 0.2s ease;
}

.password-requirements li::before {
  content: "•";
  color: #d1d5db;
  margin-right: 0.5rem;
  transition: all 0.2s ease;
}

.password-requirements li.met {
  color: #059669;
}

.password-requirements li.met::before {
  content: "✓";
  color: #059669;
  transform: scale(1.2);
}

.terms-section {
  margin-bottom: 1.5rem;
}

.terms-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
}

.terms-checkbox input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  margin-top: 0.25rem;
}

.terms-link {
  color: #1a472a;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.terms-link:hover {
  color: #2d5a3f;
  text-decoration: underline;
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

.loading-spinner {
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

.login-link {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #6b7280;
}

.login-link a {
  color: #1a472a;
  font-weight: bold;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .register-container {
    padding: 1rem;
  }

  .register-card {
    padding: 1.5rem;
  }

  .logo {
    font-size: 1.75rem;
  }

  .header h2 {
    font-size: 1.5rem;
  }
}
</style>