<template>
    <div class="password-reset-container">
        <div class="password-reset-card">
            <div class="header">
                <div class="logo">Fantasy Kenyan League</div>
                <p class="tagline">Reset your password</p>
            </div>

            <div v-if="success" class="success-alert">
                <CheckCircle class="alert-icon" />
                <p class="success-text">{{ success }}</p>
            </div>

            <div v-if="error" class="error-alert">
                <AlertCircle class="alert-icon" />
                <p class="error-text">{{ error }}</p>
            </div>

            <form
                @submit.prevent="handleResetRequest"
                class="password-reset-form"
                novalidate
            >
                <div class="form-group">
                    <label for="email">Email Address</label>
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
                        {{ v$.email.$errors[0]?.$message }}
                    </span>
                </div>

                <button
                    type="submit"
                    :disabled="isLoading || !formIsValid"
                    class="submit-button"
                >
                    <span v-if="isLoading" class="loading-spinner"></span>
                    <span v-else>Send Reset Link</span>
                </button>

                <div class="form-footer">
                    <div class="signin-wrapper">
                        <span>Remember your password?</span>
                        <router-link to="/sign-in" class="signin-link">Sign In</router-link>
                    </div>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import useVuelidate from "@vuelidate/core";
import { required, email } from "@vuelidate/validators";
import { useAuthStore } from "@/stores/auth";
import { AlertCircle, CheckCircle, XCircle, Mail } from "lucide-vue-next";

const authStore = useAuthStore();

const form = reactive({
    email: "",
});

const rules = {
    email: { required, email },
};

const v$ = useVuelidate(rules, form);

const formIsValid = computed(() => !v$.value.$error && form.email.trim() !== "");

const isLoading = ref(false);
const error = ref<string | null>(null);
const success = ref<string | null>(null);

const handleResetRequest = async () => {
    const isValid = await v$.value.$validate();

    if (!isValid) {
        return;
    }

    isLoading.value = true;
    error.value = null;

    try {
        await authStore.resetPassword(form.email);
        success.value = "Password reset link sent to your email if registered.";
        form.email = ""; // Clear the form after successful submission
    } catch (err: any) {
        error.value = err.message || "Failed to send reset link.";
    } finally {
        isLoading.value = false;
    }
};
</script>

<style scoped>
.password-reset-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    background: linear-gradient(135deg, #f0f4f8, #e0f2f1);
    font-family: "Inter", sans-serif;
}

.password-reset-card {
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
    right: 1rem;
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

.error-text {
    font-size: 0.75rem;
    color: #ef4444;
    margin-top: 0.5rem;
    display: block;
}

/* Buttons */
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

/* Form Footer */
.form-footer {
    margin-top: 1.5rem;
}

.signin-wrapper {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    font-size: 0.85rem;
}

.signin-wrapper span {
    color: #6b7280;
}

.signin-link {
    color: #1a472a;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s ease;
}

.signin-link:hover {
    color: #164624;
    text-decoration: underline;
}

/* Alert Messages */
.error-alert,
.success-alert {
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    text-align: left;
    animation: slideIn 0.3s ease;
}

.error-alert {
    background: #fee2e2;
    color: #b91c1c;
}

.success-alert {
    background: #d1fae5;
    color: #065f46;
}

.alert-icon {
    flex-shrink: 0;
    height: 1rem;
    width: 1rem;
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
    .password-reset-container {
        padding: 1rem;
    }

    .password-reset-card {
        padding: 1.5rem;
    }
}
</style>