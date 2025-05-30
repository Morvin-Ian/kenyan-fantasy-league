<template>
    <div class="password-reset-container">
        <div class="password-reset-card">
            <div class="header">
                <div class="logo">Fantasy Kenyan League</div>
                <p class="subtitle">Reset your password</p>
            </div>

            <!-- Error Alert -->
            <div v-if="error" class="alert error-alert">
                <AlertCircle class="alert-icon" />
                <p>{{ error }}</p>
                <button @click="clearError" class="dismiss-button">
                    <XCircle :size="18" />
                </button>
            </div>

            <!-- Success Alert -->
            <div v-if="success" class="alert success-alert">
                <CheckCircle class="alert-icon" />
                <p>{{ success }}</p>
                <button @click="goToLogin" class="login-button">
                    Go to Login
                </button>
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
                    <div class="input-wrapper">
                        <input
                            id="new-password"
                            v-model="form.newPassword"
                            :type="showPassword ? 'text' : 'password'"
                            placeholder="Enter your new password"
                            :class="{ error: v$.newPassword.$invalid && v$.newPassword.$dirty }"
                            @blur="v$.newPassword.$touch"
                            aria-required="true"
                        />
                        <button 
                            type="button" 
                            class="toggle-password" 
                            @click="showPassword = !showPassword"
                        >
                            <Eye v-if="!showPassword" :size="18" />
                            <EyeOff v-else :size="18" />
                        </button>
                    </div>
                    <span
                        v-if="v$.newPassword.$dirty && v$.newPassword.$invalid"
                        class="error-text"
                    >
                        <span v-if="v$.newPassword.required.$invalid">Password is required.</span>
                        <span v-if="v$.newPassword.minLength.$invalid">
                            Password must be at least 8 characters long.
                        </span>
                    </span>
                </div>

                <!-- Confirm Password Field -->
                <div class="form-group">
                    <label for="confirm-password">Confirm Password</label>
                    <div class="input-wrapper">
                        <input
                            id="confirm-password"
                            v-model="form.confirmPassword"
                            :type="showConfirmPassword ? 'text' : 'password'"
                            placeholder="Confirm your new password"
                            :class="{ error: v$.confirmPassword.$invalid && v$.confirmPassword.$dirty }"
                            @blur="v$.confirmPassword.$touch"
                            aria-required="true"
                        />
                        <button 
                            type="button" 
                            class="toggle-password" 
                            @click="showConfirmPassword = !showConfirmPassword"
                        >
                            <Eye v-if="!showConfirmPassword" :size="18" />
                            <EyeOff v-else :size="18" />
                        </button>
                    </div>
                    <span
                        v-if="v$.confirmPassword.$dirty && v$.confirmPassword.$invalid"
                        class="error-text"
                    >
                        <span v-if="v$.confirmPassword.required.$invalid">Confirm password is required.</span>
                        <span v-if="v$.confirmPassword.sameAsPassword.$invalid">
                            Passwords must match.
                        </span>
                    </span>
                </div>

                <!-- Password Strength Indicator -->
                <div v-if="form.newPassword" class="password-strength">
                    <div class="strength-label">Password strength:</div>
                    <div class="strength-meter">
                        <div 
                            class="strength-value" 
                            :style="{ width: passwordStrength + '%', backgroundColor: strengthColor }"
                        ></div>
                    </div>
                    <div class="strength-text" :style="{ color: strengthColor }">{{ strengthText }}</div>
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
                
                <div class="text-center">
                    <a @click="goToLogin" class="back-link">Back to login</a>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import useVuelidate from "@vuelidate/core";
import { AlertCircle, CheckCircle, XCircle, Eye, EyeOff } from "lucide-vue-next";
import { required, minLength, helpers } from "@vuelidate/validators";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { onMounted } from "vue";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const showPassword = ref(false);
const showConfirmPassword = ref(false);

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

const passwordStrength = computed(() => {
    const password = form.value.newPassword;
    if (!password) return 0;
    
    let strength = 0;
    
    if (password.length >= 8) strength += 20;
    if (password.length >= 12) strength += 10;
    
    if (/[A-Z]/.test(password)) strength += 20; 
    if (/[a-z]/.test(password)) strength += 10; 
    if (/[0-9]/.test(password)) strength += 20; 
    if (/[^A-Za-z0-9]/.test(password)) strength += 20; 
    
    return Math.min(strength, 100);
});

const strengthColor = computed(() => {
    const strength = passwordStrength.value;
    if (strength < 40) return '#dc2626'; 
    if (strength < 70) return '#f59e0b'; 
    return '#16a34a'; 
});

const strengthText = computed(() => {
    const strength = passwordStrength.value;
    if (strength < 40) return 'Weak';
    if (strength < 70) return 'Moderate';
    return 'Strong';
});

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
        success.value = "Password reset successfully! ";
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

onMounted(() => {
  authStore.error = null;
  if (authStore.isAuthenticated) {
    router.replace({ name: "home" });
  }
});
</script>

<style scoped>
.password-reset-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #f0f4f8, #e0f2f1);
    padding: 20px;
}

.password-reset-card {
    width: 100%;
    max-width: 450px;
    padding: 32px;
    border-radius: 16px;
    background-color: #fff;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    text-align: center;
}

.header {
    margin-bottom: 32px;
}

.logo {
    font-size: 2.25rem;
    font-weight: 800;
    color: #1a472a;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin-top: 0;
}

.alert {
    display: flex;
    align-items: center;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 24px;
    position: relative;
    text-align: left;
    animation: fadeIn 0.3s ease;
}

.error-alert {
    background: #fee2e2;
    color: #b91c1c;
    border-left: 4px solid #b91c1c;
}

.success-alert {
    background: #dcfce7;
    color: #16a34a;
    border-left: 4px solid #16a34a;
    flex-direction: column;
    align-items: flex-start;
}

.alert-icon {
    flex-shrink: 0;
    margin-right: 12px;
}

.dismiss-button {
    background: none;
    border: none;
    color: #b91c1c;
    cursor: pointer;
    padding: 4px;
    position: absolute;
    right: 12px;
    top: 12px;
}

.password-reset-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    margin-bottom: 4px;
}

.form-group label {
    font-size: 0.95rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 8px;
    display: block;
    text-align: left;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

input {
    width: 100%;
    padding: 14px;
    text-align: left;
    border: 1.5px solid #e5e7eb;
    border-radius: 10px;
    font-size: 16px;
    background-color: #f9fafb;
    transition: all 0.2s ease;
}

input:focus {
    outline: none;
    border-color: #1a472a;
    background-color: #fff;
    box-shadow: 0 0 0 3px rgba(26, 71, 42, 0.1);
}

input.error {
    border-color: #ef4444;
    background-color: #fef2f2;
}

.toggle-password {
    background: none;
    border: none;
    color: #6b7280;
    cursor: pointer;
    position: absolute;
    right: 12px;
    padding: 2px;
}

.error-text {
    font-size: 0.85rem;
    color: #ef4444;
    margin-top: 8px;
    display: block;
    text-align: left;
    animation: fadeIn 0.2s ease;
}

.password-strength {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 8px;
}

.strength-label {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 6px;
}

.strength-meter {
    width: 100%;
    height: 6px;
    background-color: #e5e7eb;
    border-radius: 3px;
    overflow: hidden;
}

.strength-value {
    height: 100%;
    transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-text {
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 6px;
    align-self: flex-end;
}

.submit-button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    background-color: #1a472a;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 12px;
}

.submit-button:disabled {
    background-color: #93c5aa;
    cursor: not-allowed;
}

.submit-button:hover:not(:disabled) {
    background-color: #143821;
    transform: translateY(-1px);
}

.submit-button:active:not(:disabled) {
    transform: translateY(0);
}

.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
}

.login-button {
    margin-top: 16px;
    padding: 10px 20px;
    background-color: #16a34a;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
}

.login-button:hover {
    background-color: #15803d;
}

.text-center {
    text-align: center;
    margin-top: 16px;
}

.back-link {
    color: #6b7280;
    text-decoration: none;
    font-size: 0.95rem;
    cursor: pointer;
    transition: color 0.2s;
}

.back-link:hover {
    color: #1a472a;
    text-decoration: underline;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>