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
                        <input
                            id="email"
                            v-model="form.email"
                            type="email"
                            required
                            placeholder="Enter your email"
                            :class="{ error: v$.email.$error }"
                            @blur="v$.email.$touch"
                        />
                        <div class="input-icon-right" v-if="form.email">
                            <CheckCircle
                                v-if="!v$.email.$error"
                                class="valid-icon"
                            />
                            <XCircle
                                v-else
                                class="invalid-icon"
                            />
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
                        <input
                            id="password"
                            v-model="form.password"
                            :type="showPassword ? 'text' : 'password'"
                            required
                            placeholder="Enter your password"
                            :class="{ error: v$.password.$error }"
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
                    <span
                        v-if="authStore.isLoading"
                        class="loading-spinner"
                    ></span>
                    <span v-else>Sign In</span>
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
        router.push({ path: "/" });
    } catch (error) {
        console.error("Sign-in failed:", error);
    }
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