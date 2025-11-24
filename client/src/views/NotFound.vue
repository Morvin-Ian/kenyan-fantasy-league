<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code animate-fade-in">404</div>
      <h1 class="error-title animate-slide-up">Page Not Found</h1>
      <p class="error-message animate-slide-up" :style="{ animationDelay: '100ms' }">
        The KPL fantasy page you're looking for doesn't exist or has been moved.
      </p>
      <div class="action-buttons animate-slide-up" :style="{ animationDelay: '200ms' }">
        <router-link to="/" class="home-button">
          Return to KPL Home
        </router-link>
        <button @click="goBack" class="back-button">
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  window.history.length > 1 ? router.go(-1) : router.push('/');
};
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 16px;
  background: linear-gradient(to bottom right, #f3f4f6, #e5e7eb);
}

.not-found-content {
  max-width: 500px;
  width: 100%;
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 32px 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.not-found-content:hover {
  transform: translateY(-5px);
}

.error-code {
  font-size: 6rem;
  font-weight: 800;
  background: linear-gradient(90deg, #1f2937, #4b5563, #6b7280);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 300% 300%;
  animation: gradientText 5s ease infinite;
  margin: 0 0 12px 0;
  line-height: 1;
  letter-spacing: -2px;
  text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.05);
}

@keyframes gradientText {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.error-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.error-message {
  font-size: 1rem;
  color: #4b5563;
  margin-bottom: 24px;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.home-button,
.back-button {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.home-button {
  background: #1f2937;
  color: white;
  border: none;
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.home-button:hover {
  background: #111827;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.back-button {
  background: white;
  color: #1f2937;
  border: 2px solid #1f2937;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.back-button:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

@media (max-width: 640px) {
  .not-found-content {
    padding: 24px 16px;
  }

  .error-code {
    font-size: 4.5rem;
  }

  .error-title {
    font-size: 1.5rem;
  }

  .error-message {
    font-size: 0.9rem;
  }

  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }

  .home-button,
  .back-button {
    width: 100%;
    padding: 10px 16px;
  }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}
</style>