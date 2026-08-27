<template>
    <div class="oauth-callback-container">
        <div class="callback-card">
            <div v-if="isProcessing" class="processing-state">
                <div class="spinner"></div>
                <h2>Completing Sign In...</h2>
                <p>Please wait while we authenticate your account</p>
            </div>

            <div v-else-if="error" class="error-state">
                <div class="error-icon">⚠️</div>
                <h2>Authentication Failed</h2>
                <p>{{ errorMessage }}</p>
                <button @click="redirectToSignIn" class="retry-button">
                    Return to Sign In
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import apiClient from "@/axios-interceptor";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isProcessing = ref(true);
const error = ref(false);
const errorMessage = ref("");

const redirectToSignIn = () => {
    router.push({ name: "sign-in" });
};

const redirectToHome = () => {
    router.push({ name: "home" });
};

onMounted(async () => {
    // Snapshot the query first, then immediately scrub it from the address
    // bar and browser history so the one-time auth code never lingers.
    const query = { ...route.query };
    history.replaceState({}, "", window.location.pathname);

    try {
        const authSuccess = query.auth_success === "true";
        const authMessage = query.auth_message as string;
        const authCode = query.auth_code as string;

        // The Google callback redirects with ?tokens=...&user=... in the URL.
        // Both JWTs must not persist in the address bar, history, access logs
        // or Referer headers — scrub the query string immediately, before any
        // async work or navigation. See docs/incidents/785cd6ee6d3241ee.md.
        history.replaceState({}, "", window.location.pathname);

        if (!authSuccess) {
            throw new Error(authMessage || "Authentication failed");
        }

        if (!authCode) {
            throw new Error("Missing authentication data");
        }

        // Exchange the one-time code for tokens over POST. The tokens come
        // back in the response body — they are never carried in the URL.
        const { data } = await apiClient.post("/auth/google/token/", {
            auth_code: authCode,
        });

        authStore.setToken(data.access, data.refresh);
        authStore.setUser(data.user);

        await new Promise((resolve) => setTimeout(resolve, 1000));

        redirectToHome();
    } catch (err: any) {
        console.error("OAuth callback error:", err);
        isProcessing.value = false;
        error.value = true;
        errorMessage.value = err.message || "An unexpected error occurred";

        setTimeout(() => {
            redirectToSignIn();
        }, 5000);
    }
});
</script>

<style scoped>
.oauth-callback-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    background: linear-gradient(135deg, #f0f4f8, #e0f2f1);
    font-family: 'Segoe UI', system-ui, sans-serif;
}

.callback-card {
    background: #ffffff;
    padding: 3rem;
    border-radius: 1rem;
    width: 100%;
    max-width: 450px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    text-align: center;
}

/* Processing State */
.processing-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

.spinner {
    width: 3rem;
    height: 3rem;
    border: 4px solid rgba(26, 71, 42, 0.1);
    border-radius: 50%;
    border-top-color: #1a472a;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.processing-state h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a472a;
    margin: 0;
}

.processing-state p {
    color: #6b7280;
    font-size: 0.95rem;
    margin: 0;
}

/* Error State */
.error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

.error-icon {
    font-size: 3rem;
}

.error-state h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #dc2626;
    margin: 0;
}

.error-state p {
    color: #6b7280;
    font-size: 0.95rem;
    margin: 0;
    max-width: 350px;
}

.retry-button {
    margin-top: 1rem;
    padding: 0.875rem 2rem;
    background: #1a472a;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 1rem;
}

.retry-button:hover {
    background: #164624;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.retry-button:active {
    transform: translateY(0);
    box-shadow: none;
}

/* Responsive Design */
@media (max-width: 640px) {
    .oauth-callback-container {
        padding: 1rem;
    }

    .callback-card {
        padding: 2rem;
    }
}
</style>
