<template>
    <div class="signin-container">
        <div class="signin-card">
            <div class="header">
                <div class="logo">Fantasy Kenyan League</div>
                <p class="tagline">Sign in to manage your team</p>
            </div>

            <div v-if="authStore.error" class="error-alert">
                <AlertCircle class="alert-icon" />
                <p>{{ authStore.error }}</p>
            </div>

            <form @submit.prevent="handleSubmit" class="signin-form" novalidate>
                <div class="form-group">
                    <label for="email">Email address</label>
                    <div class="input-wrapper">
                        <Mail class="input-icon-left" />
                        <input id="email" v-model="form.email" type="email" required placeholder="Enter your email"
                            :class="{ error: v$.email.$error }" @blur="v$.email.$touch" />
                        <div class="input-icon-right" v-if="form.email">
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
                        <Lock class="input-icon-left" />
                        <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" required
                            placeholder="Enter your password" :class="{ error: v$.password.$error }"
                            @blur="v$.password.$touch" />
                        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                            <Eye v-if="!showPassword" />
                            <EyeOff v-else />
                        </button>
                    </div>
                    <span v-if="v$.password.$error" class="error-text">
                        {{ v$.password.$errors[0].$message }}
                    </span>
                </div>

                <button type="submit" :disabled="authStore.isLoading || !formIsValid" class="submit-button">
                    <span v-if="authStore.isLoading" class="loading-spinner"></span>
                    <span v-else>Sign In</span>
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

                <div class="form-footer">
                    <router-link to="/password/reset/request" class="forgot-password-link">
                        Forgot Password?
                    </router-link>

                    <div class="register-wrapper">
                        <span>Don't have an account?</span>
                        <router-link to="/sign-up" class="register-link">Create one</router-link>
                    </div>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import {
    AlertCircle,
    CheckCircle,
    XCircle,
    Eye,
    EyeOff,
    Mail,
    Lock
} from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth";
import useVuelidate from "@vuelidate/core";
import { required, email } from "@vuelidate/validators";
import { onMounted } from "vue";

const router = useRouter();
const authStore = useAuthStore();

const showPassword = ref(false);

const form = reactive({
    email: "",
    password: "",
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
        if (!authStore.error) {
            router.push({ path: "/" });
        }
    } catch (error: any) {
        console.error("Sign-in failed:", error);
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
.signin-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    background: linear-gradient(135deg, #f0f4f8, #e0f2f1);
    font-family: 'Segoe UI', system-ui, sans-serif;
}

.signin-card {
    background: #ffffff;
    padding: 2.5rem;
    border-radius: 1rem;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    text-align: center;
}

/* Header */
.logo {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a472a;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.tagline {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

/* Form Group */
.form-group {
    margin-bottom: 1.5rem;
    text-align: left;
}

.form-group label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #4b5563;
    margin-bottom: 0.5rem;
    display: block;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon-left {
    position: absolute;
    left: 1rem;
    color: #9ca3af;
    height: 1rem;
    width: 1rem;
}

.input-wrapper input {
    width: 100%;
    padding: 0.8rem 1rem 0.8rem 2.5rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    background: #ffffff;
}

.input-wrapper input:hover {
    border-color: #d1d5db;
}

.input-wrapper input:focus {
    outline: none;
    border-color: #1a472a;
    box-shadow: 0 0 0 3px rgba(26, 71, 42, 0.1);
}

.input-wrapper input.error {
    border-color: #ef4444;
    background: #fef2f2;
}

.input-icon-right {
    position: absolute;
    right: 2.5rem;
    color: #9ca3af;
}

.valid-icon {
    color: #10b981;
    height: 1rem;
    width: 1rem;
}

.invalid-icon {
    color: #ef4444;
    height: 1rem;
    width: 1rem;
}

.toggle-password {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.toggle-password:hover {
    color: #4b5563;
}

.toggle-password svg {
    height: 1rem;
    width: 1rem;
}

.error-text {
    font-size: 0.75rem;
    color: #ef4444;
    margin-top: 0.5rem;
    display: block;
}

.submit-button {
    width: 100%;
    padding: 0.8rem;
    background: #1a472a;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 2.75rem;
}

.submit-button:hover {
    background: #164624;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.submit-button:active {
    transform: translateY(0);
    box-shadow: none;
}

.submit-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
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

/* Divider */
.divider {
    display: flex;
    align-items: center;
    margin: 1.5rem 0;
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
    padding: 0.8rem;
    background: #ffffff;
    color: #3c4043;
    font-weight: 500;
    border: 1px solid #dadce0;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.75rem;
    height: 2.75rem;
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

.form-footer {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.forgot-password-link {
    color: #1a472a;
    font-weight: 500;
    text-decoration: none;
    font-size: 0.85rem;
    transition: color 0.2s ease;
    align-self: flex-end;
}

.forgot-password-link:hover {
    color: #164624;
    text-decoration: underline;
}

.register-wrapper {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

.register-wrapper span {
    color: #6b7280;
}

.register-link {
    color: #1a472a;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s ease;
}

.register-link:hover {
    color: #164624;
    text-decoration: underline;
}

/* Error Alert */
.error-alert {
    background: #fee2e2;
    color: #b91c1c;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    text-align: left;
}

.alert-icon {
    flex-shrink: 0;
    height: 1rem;
    width: 1rem;
}

/* Responsive Design */
@media (max-width: 640px) {
    .signin-container {
        padding: 1rem;
    }

    .signin-card {
        padding: 1.5rem;
    }
}
</style>