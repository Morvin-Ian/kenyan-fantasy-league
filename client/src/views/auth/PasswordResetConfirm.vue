<template>
    <div class="password-reset-container">
        <div class="password-reset-card">
            <div class="header">
                <div class="logo">Fantasy Kenyan League</div>
            </div>

            <!-- Error Alert with Dismiss Button -->
            <div v-if="error" class="error-alert">
                <AlertCircle class="alert-icon" />
                <p>{{ error }}</p>
            </div>

            <!-- Success Alert -->
            <div v-if="success" class="success-alert">
                <p>{{ success }}</p>
                <button @click="goToLogin">Go to Login</button>
            </div>

            <!-- Password Reset Form -->
            <form
                v-if="!success"
                @submit.prevent="handleResetConfirm"
                class="password-reset-form"
                novalidate
            >
                <!-- New Password Field -->
                <div class="form-group">
                    <label for="new-password">New Password</label>
                    <input
                        id="new-password"
                        v-model="form.newPassword"
                        type="password"
                        placeholder="Enter your new password"
                        :class="{
                            error:
                                v$.newPassword.$invalid &&
                                v$.newPassword.$dirty,
                        }"
                        @blur="v$.newPassword.$touch"
                        aria-required="true"
                    />
                    <span
                        v-if="v$.newPassword.$dirty && v$.newPassword.$invalid"
                        class="error-text"
                    >
                        <span v-if="v$.newPassword.required.$invalid"
                            >Password is required.</span
                        >
                        <span v-if="v$.newPassword.minLength.$invalid">
                            Password must be at least 8 characters long.
                        </span>
                    </span>
                </div>

                <!-- Confirm Password Field -->
                <div class="form-group">
                    <label for="confirm-password">Confirm Password</label>
                    <input
                        id="confirm-password"
                        v-model="form.confirmPassword"
                        type="password"
                        placeholder="Confirm your new password"
                        :class="{
                            error:
                                v$.confirmPassword.$invalid &&
                                v$.confirmPassword.$dirty,
                        }"
                        @blur="v$.confirmPassword.$touch"
                        aria-required="true"
                    />
                    <span
                        v-if="
                            v$.confirmPassword.$dirty &&
                            v$.confirmPassword.$invalid
                        "
                        class="error-text"
                    >
                        <span v-if="v$.confirmPassword.required.$invalid"
                            >Confirm password is required.</span
                        >
                        <span
                            v-if="v$.confirmPassword.sameAsNewPassword.$invalid"
                        >
                            Passwords must match.
                        </span>
                    </span>
                </div>

                <!-- Submit Button -->
                <button
                    type="submit"
                    :disabled="isLoading || v$.$invalid"
                    class="submit-button"
                >
                    <span v-if="isLoading" class="loading-spinner"></span>
                    <span v-else>Reset Password</span>
                </button>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import useVuelidate from "@vuelidate/core";
import { AlertCircle } from "lucide-vue-next";
import { required, minLength, helpers } from "@vuelidate/validators";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const form = ref({
    newPassword: "",
    confirmPassword: "",
});

const rules = {
    newPassword: {
        required,
        minLength: minLength(8),
    },
    confirmPassword: {
        required,
        sameAsPassword: helpers.withMessage(
            "Passwords must match",
            (value) => value === form.value.newPassword,
        ),
    },
};

const v$ = useVuelidate(rules, form);

const isLoading = ref(false);
const error = ref<string | null>(null);
const success = ref<string | null>(null);

const formIsValid = computed(() => !v$.$invalid);

const handleResetConfirm = async () => {
    isLoading.value = true;
    error.value = null;

    const resetData = {
        new_password: form.value.newPassword,
        re_new_password: form.value.confirmPassword,
        uid: route.params.uid as string,
        token: route.params.token as string,
    };

    try {
        await authStore.resetPasswordConfirm(resetData);
        success.value = "Password reset successfully! You can now log in.";
        form.value.newPassword = "";
        form.value.confirmPassword = "";
    } catch (err: any) {
        console.log(err);
        error.value = err.message || "Failed to reset password.";
    } finally {
        isLoading.value = false;
    }
};

const clearError = () => {
    error.value = null;
};

const goToLogin = () => {
    router.push("/sign-in");
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
    display: block;
    text-align: left;
}

input {
    width: 100%;
    padding: 10px;
    text-align: left;
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
