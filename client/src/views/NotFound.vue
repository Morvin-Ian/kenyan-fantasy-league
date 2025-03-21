<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-illustration">
        <div class="error-code">404</div>
        <div class="error-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 16V12M12 8H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" 
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-message">The page you're looking for doesn't exist or has been moved to another URL.</p>
      <div class="action-buttons">
        <router-link to="/" class="home-button primary-button">
          <span class="button-icon">←</span> Return Home
        </router-link>
        <button @click="goBack" class="back-button secondary-button">
          Go Back
        </button>
      </div>
      <div class="search-section">
        <p class="search-prompt">Or try searching for what you need:</p>
        <div class="search-container">
          <input type="text" class="search-input" placeholder="Search..." v-model="searchQuery">
          <button class="search-button" @click="performSearch">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" 
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "NotFound",
  data() {
    return {
      searchQuery: ""
    };
  },
  methods: {
    goBack() {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/');
    },
    performSearch() {
      if (this.searchQuery.trim()) {
        // Navigate to search page with query
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
  background-color: #f8f9fa;
  padding: 20px;
  background-image: linear-gradient(135deg, #f8f9fa 25%, #eef1f5 25%, #eef1f5 50%, #f8f9fa 50%, #f8f9fa 75%, #eef1f5 75%, #eef1f5 100%);
  background-size: 40px 40px;
}

.not-found-content {
  max-width: 550px;
  width: 100%;
  text-align: center;
  background-color: white;
  border-radius: 16px;
  padding: 50px 40px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
}

.error-illustration {
  position: relative;
  height: 120px;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.error-code {
  font-size: 7rem;
  font-weight: 800;
  color: #00868b;
  opacity: 0.15;
  margin: 0;
  line-height: 1;
  letter-spacing: -2px;
}

.error-icon {
  position: absolute;
  width: 60px;
  height: 60px;
  color: #00868b;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.error-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 15px 0;
}

.error-message {
  font-size: 1.15rem;
  color: #718096;
  margin-bottom: 30px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 30px;
}

.primary-button, .secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 50px;
  text-decoration: none;
  transition: all 0.3s ease;
  min-width: 140px;
}

.primary-button {
  background-color: #00868b;
  color: white;
  border: none;
}

.primary-button:hover {
  background-color: #006d72;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 134, 139, 0.2);
}

.secondary-button {
  background-color: transparent;
  color: #00868b;
  border: 2px solid #00868b;
  cursor: pointer;
}

.secondary-button:hover {
  background-color: rgba(0, 134, 139, 0.05);
  transform: translateY(-2px);
}

.button-icon {
  margin-right: 8px;
  font-size: 1.1rem;
}

.search-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.search-prompt {
  font-size: 1rem;
  color: #718096;
  margin-bottom: 15px;
}

.search-container {
  display: flex;
  max-width: 400px;
  margin: 0 auto;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 50px 0 0 50px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #00868b;
}

.search-button {
  width: 48px;
  background-color: #00868b;
  color: white;
  border: none;
  border-radius: 0 50px 50px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-button svg {
  width: 20px;
  height: 20px;
}

.search-button:hover {
  background-color: #006d72;
}

@media (max-width: 640px) {
  .not-found-content {
    padding: 40px 20px;
  }
  
  .error-code {
    font-size: 5rem;
  }
  
  .error-icon {
    width: 50px;
    height: 50px;
  }
  
  .error-title {
    font-size: 1.8rem;
  }
  
  .error-message {
    font-size: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .primary-button, .secondary-button {
    width: 100%;
  }
}
</style>