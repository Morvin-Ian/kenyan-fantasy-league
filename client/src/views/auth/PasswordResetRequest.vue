<template>
    <div class="password-reset-container">
        <div class="password-reset-card">
            <div class="header">
                <div class="logo">Fantasy Kenyan League</div>
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
                        <input
                            id="email"
                            v-model="form.email"
                            type="email"
                            required
                            placeholder="Enter your email"
                            :class="{ 'is-invalid': v$.email.$error }"
                        />
                    </div>
                    <p v-if="v$.email.$error" class="error-text">
                        {{ v$.email.$errors[0]?.$message }}
                    </p>
                </div>

                <button
                    type="submit"
                    :disabled="isLoading || !email"
                    class="submit-button"
                >
                    <span v-if="isLoading" class="loading-spinner"></span>
                    <span v-else>Send Reset Link</span>
                </button>

                <p class="signin-link text-end">
                    Remember your password?
                    <router-link to="/sign-in">Sign In</router-link>
                </p>
            </form>
        </div>
    </div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import useVuelidate from "@vuelidate/core";
import { required, email } from "@vuelidate/validators";
import { useAuthStore } from "@/stores/auth";
import { AlertCircle } from "lucide-vue-next";

const authStore = useAuthStore();

const form = ref({
    email: "",
});

const rules = {
    email: { required, email },
};

const v$ = useVuelidate(rules, form);

const isLoading = ref(false);
const error = ref<string | null>(null);

const handleResetRequest = async () => {
    const isValid = await v$.value.$validate();

    if (!isValid) {
        return;
    }

    isLoading.value = true;
    error.value = null;

    try {
        await authStore.resetPassword(form.value.email);
        alert("Password reset link sent to your email.");
    } catch (err: any) {
        error.value = err.message || "Failed to send reset link.";
    } finally {
        isLoading.value = false;
    }
};
</script>

<style scoped>
.password-reset-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f4f5f7;
}

.password-reset-card {
    width: 100%;
    max-width: 400px;
    padding: 25px;
    border-radius: 8px;
    background-color: #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.logo {
    font-size: 2rem;
    font-weight: 700;
    color: #1a472a;
    margin-bottom: 1.5rem;
    letter-spacing: -0.5px;
}
.password-reset-form {
    display: flex;
    flex-direction: column;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
    text-align: left;
    display: block;
}

input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
}

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

.error-text {
    font-size: 0.8rem;
    color: #ef4444;
    margin-top: 0.5rem;
    display: block;
    animation: fadeIn 0.2s ease;
}
.submit-button {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: bold;
    color: #fff;
    background-color: #1a472a;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.submit-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.submit-button:hover:not(:disabled) {
    background-color: #164624;
}

.text-end {
    margin-top: 15px;
    text-align: right;
}

.signin-link {
    font-size: 14px;
    color: #555;
}

.signin-link a {
    color: #007bff;
    text-decoration: none;
}
</style>
