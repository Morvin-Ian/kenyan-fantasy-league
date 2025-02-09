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
                            :class="{ error: v$.email.$error }"
                            @blur="v$.email.$touch"
                        />
                        <div class="input-icon" v-if="form.email">
                            <CheckCircle
                                v-if="!v$.email.$error"
                                class="valid-icon h-4"
                            />
                            <XCircle
                                v-else
                                class="invalid-icon h-4 text-red-400"
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

                <!-- Forgot Password Link -->
                <p class="forgot-password-link text-end mt-3 text-sm">
                    <router-link to="/password/reset/request"
                        >Forgot Password?</router-link
                    >
                </p>

                <p class="register-link text-end">
                    Don't have an account?
                    <router-link to="/sign-up">Create one</router-link>
                </p>
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
    background: linear-gradient(135deg, #f0f4f8, #ffffff);
    font-family: "Inter", sans-serif;
}

.signin-card {
    background: #ffffff;
    padding: 2.5rem;
    border-radius: 1.5rem;
    width: 100%;
    max-width: 450px;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    text-align: center;
    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease;
}

.signin-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

/* Header */
.logo {
    font-size: 2rem;
    font-weight: 700;
    color: #1a472a;
    margin-bottom: 1.5rem;
    letter-spacing: -0.5px;
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
    padding: 0.9rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.75rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    background: #f9fafb;
}

.input-wrapper input:hover {
    border-color: #d1d5db;
}

.input-wrapper input:focus {
    outline: none;
    border-color: #1a472a;
    box-shadow: 0 0 0 3px rgba(26, 71, 42, 0.1);
    background: white;
}

.input-wrapper input.error {
    border-color: #ef4444;
    background: #fef2f2;
}

.input-icon {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #9ca3af;
}

.toggle-password {
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 0.5rem;
    transition: color 0.2s ease;
}

.toggle-password:hover {
    color: #1a472a;
}

.error-text {
    font-size: 0.8rem;
    color: #ef4444;
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

/* Buttons */
.submit-button {
    width: 100%;
    padding: 0.9rem;
    background: #1a472a;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.submit-button:hover {
    background: #164624;
    transform: translateY(-2px);
}

.submit-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
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

/* Register Link */
.register-link {
    margin-top: 1.5rem;
    font-size: 0.9rem;
    color: #6b7280;
    text-align: center;
}

.register-link a {
    color: #1a472a;
    font-weight: bold;
    text-decoration: none;
    transition: color 0.2s ease;
}

.register-link a:hover {
    color: #2d5a3f;
    text-decoration: underline;
}

/* Error Alert */
.error-alert {
    background: #fee2e2;
    color: #b91c1c;
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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

/* Responsive Design */
@media (max-width: 640px) {
    .signin-container {
        padding: 1rem;
    }

    .signin-card {
        padding: 1.5rem;
    }

    .logo {
        font-size: 1.75rem;
    }

    .input-wrapper input {
        padding: 0.8rem;
    }

    .submit-button {
        padding: 0.8rem;
    }
}
</style>
