<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="error-title">Page Not Found</h1>
      <p class="error-message">The page you're looking for doesn't exist or has been moved.</p>
      
      <div class="action-buttons">
        <router-link to="/" class="home-button">
          Return Home
        </router-link>
        <button @click="goBack" class="back-button">
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "NotFound",
  data() {
    return {
      searchQuery: "",
      showSearch: false
    };
  },
  methods: {
    goBack() {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/');
    },
    performSearch() {
      if (this.searchQuery.trim()) {
        this.$router.push({ path: '/search', query: { q: this.searchQuery } });
      }
    }
  }
};
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: rgb(240, 255, 245);
}

.not-found-content {
  max-width: 500px;
  width: 100%;
  text-align: center;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 40px 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(107, 212, 136, 0.2);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.not-found-content:hover {
  transform: translateY(-5px);
}

.error-code {
  font-size: 7rem;
  font-weight: 800;
  background: linear-gradient(90deg, #2ecc71, #27ae60, #16a085, #1abc9c);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 300% 300%;
  animation: gradientText 5s ease infinite;
  margin: 0 0 10px 0;
  line-height: 1;
  letter-spacing: -2px;
  text-shadow: 4px 4px 0px rgba(0, 0, 0, 0.05);
}

@keyframes gradientText {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.error-title {
  font-size: 2.4rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 15px 0;
}

.error-message {
  font-size: 1.2rem;
  color: #555;
  margin-bottom: 30px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.home-button, .back-button {
  padding: 14px 28px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.home-button {
  background: linear-gradient(45deg, #2ecc71, #27ae60);
  color: white;
  border: none;
  text-decoration: none;
  box-shadow: 0 6px 15px rgba(46, 204, 113, 0.3);
}

.home-button:hover {
  background: linear-gradient(45deg, #27ae60, #1e8449);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(46, 204, 113, 0.4);
}

.back-button {
  background-color: white;
  color: #27ae60;
  border: 2px solid #27ae60;
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.1);
}

.back-button:hover {
  background-color: rgba(46, 204, 113, 0.08);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(46, 204, 113, 0.2);
}

@media (max-width: 640px) {
  .not-found-content {
    padding: 30px 20px;
  }
  
  .error-code {
    font-size: 5rem;
  }
  
  .error-title {
    font-size: 1.8rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .home-button, .back-button {
    width: 100%;
  }
}
</style>